import json, secrets, time, hmac, hashlib, requests
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.conf import settings
from .forms import SignupForm
from .models import Profile, Transaction
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

def home(request):
    return render(request,'home.html')

def register_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            login(request, user)
            return redirect('dashboard')
    else:
        form = SignupForm()
    return render(request,'register.html',{'form':form})

def login_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user:
            login(request,user)
            return redirect('dashboard')
    return render(request,'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def dashboard(request):
    profile = Profile.objects.get(user=request.user)
    txs = Transaction.objects.filter(user=request.user).order_by('-created_at')[:20]
    return render(request,'dashboard.html',{'profile':profile,'txs':txs})

@login_required
def games(request):
    return render(request,'games.html')

@login_required
def play_game(request, game):
    profile = Profile.objects.get(user=request.user)
    cost = 1
    if profile.credits < cost:
        return render(request,'play_result.html',{'message':'Solde insuffisant','profile':profile})
    import random
    reward = 0; msg = ''
    if game=='cards':
        card = random.choice(['hearts','diamonds','spades','clubs'])
        if card in ['hearts','diamonds']:
            reward = random.randint(10,30)
            msg = f'Bonne carte ({card}) ! +{reward} crédits'
        else:
            reward = -10
            msg = 'Mauvaise carte ! -10 crédits'
    elif game=='domino':
        a,b = random.randint(0,6), random.randint(0,6)
        if a==b:
            reward = 25; msg = f'Double {a}! +25 crédits'
        else:
            reward = -5; msg = f'Domino {a}|{b} - perdu -5'
    elif game=='superstar':
        slots = ['🍒','🍋','🍉','💎','7']
        spin = [random.choice(slots) for _ in range(3)]
        if len(set(spin))==1:
            reward = 200; msg = f'Jackpot {"".join(spin)} +200'
        else:
            reward = -15; msg = f'{" ".join(spin)} - perdu -15'
    else:
        return redirect('games')

    profile.credits += reward
    profile.score += max(0, reward//10)
    profile.save()
    tx = Transaction.objects.create(tx_ref=f"GAME-{int(time.time()*1000)}-{secrets.token_hex(3)}",
                                    user=request.user, provider='game', amount=reward, status='success', metadata={'game':game})
    return render(request,'play_result.html',{'message':msg,'profile':profile})

@login_required
def wallet(request):
    profile = Profile.objects.get(user=request.user)
    txs = Transaction.objects.filter(user=request.user).order_by('-created_at')[:50]
    return render(request,'wallet.html',{'profile':profile,'txs':txs})

@login_required
def deposit(request):
    if request.method=='POST':
        amt = int(request.POST.get('amount',0))
        phone = request.POST.get('phone','')
        # create a pending tx
        txref = f"MC-{int(time.time()*1000)}-{secrets.token_hex(3)}"
        tx = Transaction.objects.create(tx_ref=txref, user=request.user, provider='moncash', amount=amt, status='pending', metadata={'phone':phone})
        # If MonCash creds provided, initiate a payment request and return payment_url (sandbox)
        if settings.MONCASH_CLIENT_ID and settings.MONCASH_CLIENT_SECRET:
            token = get_moncash_token()
            if token.get('ok'):
                create = create_moncash_payment(token['token'], txref, amt, phone)
                if create.get('ok'):
                    # record provider_ref
                    tx.metadata.update({'create_response': create.get('resp')})
                    tx.save()
                    # redirect user to payment_url if provided (checkout)
                    if create.get('payment_url'):
                        return redirect(create['payment_url'])
        # else keep pending for admin approval
        return redirect('wallet')
    return redirect('wallet')

def get_moncash_token():
    base = settings.MONCASH_API_BASE.rstrip('/') if settings.MONCASH_API_BASE else ''
    if not base:
        return {'ok':False,'error':'no_base'}
    try:
        url = base + '/oauth/token'
        r = requests.post(url, auth=(settings.MONCASH_CLIENT_ID, settings.MONCASH_CLIENT_SECRET), data={'grant_type':'client_credentials'}, timeout=10)
        if r.status_code!=200:
            return {'ok':False,'error':r.text}
        j = r.json()
        return {'ok':True,'token':j.get('access_token')}
    except Exception as e:
        return {'ok':False,'error':str(e)}

def create_moncash_payment(token, merchant_ref, amount, phone):
    base = settings.MONCASH_API_BASE.rstrip('/')
    try:
        url = base + '/payments'
        headers = {'Authorization': f'Bearer {token}', 'Content-Type':'application/json'}
        payload = {
            "amount": amount,
            "merchant_ref": merchant_ref,
            "customer_msisdn": phone,
            "description": "Djoonjack deposit",
            "return_url": "",
            "cancel_url": ""
        }
        r = requests.post(url, json=payload, headers=headers, timeout=10)
        if r.status_code not in (200,201):
            return {'ok':False,'error':r.text}
        jr = r.json()
        return {'ok':True,'resp': jr, 'payment_url': jr.get('payment_url') or jr.get('checkout_url')}
    except Exception as e:
        return {'ok':False,'error':str(e)}

@csrf_exempt
def moncash_webhook(request):
    # verify signature if webhook secret set
    payload = request.body
    sig = request.headers.get('X-Moncash-Signature','') or request.headers.get('X-Signature','')
    if settings.MONCASH_WEBHOOK_SECRET:
        expected = hmac.new(settings.MONCASH_WEBHOOK_SECRET.encode(), payload, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, sig):
            return JsonResponse({'ok':False,'error':'invalid_signature'}, status=401)
    try:
        data = json.loads(payload.decode('utf-8'))
        merchant_ref = data.get('merchant_ref') or data.get('merchantReference')
        status = (data.get('status') or '').lower()
        provider_ref = data.get('provider_ref') or data.get('providerReference') or data.get('id')
        if not merchant_ref:
            return JsonResponse({'ok':False,'error':'no_ref'}, status=400)
        tx = Transaction.objects.filter(tx_ref=merchant_ref).first()
        if not tx:
            return JsonResponse({'ok':False,'error':'tx_not_found'}, status=404)
        if status in ('success','paid','completed'):
            tx.status='success'
            tx.metadata.update({'provider_ref':provider_ref, 'webhook':data})
            tx.save()
            if tx.user:
                prof = Profile.objects.get(user=tx.user); prof.credits += tx.amount; prof.save()
            return JsonResponse({'ok':True})
        elif status in ('failed','declined'):
            tx.status='failed'; tx.save(); return JsonResponse({'ok':True})
        else:
            tx.metadata.update({'webhook':data}); tx.save(); return JsonResponse({'ok':True})
    except Exception as e:
        return JsonResponse({'ok':False,'error':str(e)}, status=500)