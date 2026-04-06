# 🐙 Octopus AI — Complete Launch Guide
## From Zero to Live in 30 Minutes (No Experience Needed)

---

## WHAT YOU'LL END UP WITH
- ✅ Live website at a real URL (e.g. your-name.vercel.app or octopusai.com)
- ✅ Fully working AI chat powered by Claude
- ✅ Secure — your API key hidden from the public
- ✅ Free hosting (Vercel free tier)
- ✅ Automatic HTTPS/SSL
- ✅ Professional domain (optional, ~$10/year)

---

## STEP 1 — GET YOUR ANTHROPIC API KEY (5 min)

This is what gives Octopus AI its intelligence.

1. Go to: https://console.anthropic.com
2. Click "Sign Up" and create a free account
3. Verify your email
4. Go to "API Keys" in the left sidebar
5. Click "Create Key"
6. Name it: "octopus-ai-production"
7. COPY the key — it starts with "sk-ant-..."
   ⚠️ SAVE IT SOMEWHERE SAFE. You only see it once.

8. Add billing credit:
   - Go to "Billing" in the sidebar
   - Add $10–$20 to start
   - This gives you roughly 200,000+ messages at normal usage

---

## STEP 2 — SET UP YOUR PROJECT FILES (5 min)

You have 3 files to work with:
- index.html    ← The app interface
- api/chat.js   ← The secure backend (hides your API key)
- vercel.json   ← Deployment config

These are ready to deploy as-is.

---

## STEP 3 — CREATE A FREE VERCEL ACCOUNT (3 min)

Vercel is where your app will live. It's free and used by millions.

1. Go to: https://vercel.com
2. Click "Sign Up"
3. Sign up with GitHub (recommended) OR email
4. If using GitHub: authorize Vercel to access your account

---

## STEP 4 — INSTALL VERCEL CLI (2 min)

This lets you deploy from your computer with one command.

Open Terminal (Mac) or Command Prompt (Windows) and type:

```
npm install -g vercel
```

Don't have Node.js? Install it first from: https://nodejs.org
(Download the "LTS" version, install it, then run the command above)

Verify it worked:
```
vercel --version
```

---

## STEP 5 — DEPLOY YOUR APP (5 min)

1. Put all 3 files in a folder called "octopus-ai" on your desktop:
   ```
   octopus-ai/
   ├── index.html
   ├── vercel.json
   ├── package.json
   └── api/
       └── chat.js
   ```

2. Open Terminal and navigate to the folder:
   ```
   cd Desktop/octopus-ai
   ```

3. Login to Vercel:
   ```
   vercel login
   ```
   Follow the prompts (check your email for a link to click)

4. Deploy:
   ```
   vercel
   ```
   
   Answer the questions:
   - "Set up and deploy?" → Y
   - "Which scope?" → your username
   - "Link to existing project?" → N
   - "Project name?" → octopus-ai (or any name)
   - "In which directory is your code?" → ./ (just press Enter)
   - "Want to override settings?" → N

5. It will give you a URL like: https://octopus-ai-abc123.vercel.app
   Open it — but the AI won't work yet until Step 6!

---

## STEP 6 — ADD YOUR SECRET API KEY (3 min)

NEVER put your API key in the code. This step stores it safely.

1. Go to: https://vercel.com/dashboard
2. Click on your "octopus-ai" project
3. Click "Settings" tab
4. Click "Environment Variables" in the left menu
5. Add a new variable:
   - Name:  ANTHROPIC_API_KEY
   - Value: (paste your sk-ant-... key here)
   - Environment: check Production, Preview, and Development
6. Click "Save"

7. Redeploy for the variable to take effect:
   ```
   vercel --prod
   ```

Your app is now LIVE and SECURE! 🎉

---

## STEP 7 — TEST YOUR LIVE APP (2 min)

1. Open your Vercel URL
2. Type "Build me a landing page for a fitness app" 
3. You should see Octopus AI streaming a response!

If it works — congratulations! You have a live AI product.

---

## STEP 8 (OPTIONAL) — ADD A CUSTOM DOMAIN (~10 min, ~$10/year)

Recommended domains for your brand:
- octopusai.app (~$14/year at Namecheap)
- tryoctopus.ai (~$60/year)
- useoctopus.com (~$12/year)
- octopuscreate.com (~$12/year)

Where to buy: https://www.namecheap.com (cheapest, recommended)

After buying:
1. Go to Vercel dashboard → your project → Settings → Domains
2. Click "Add Domain"
3. Type your domain (e.g. octopusai.app)
4. Vercel will show you DNS records to add
5. Go to Namecheap → Manage Domain → Advanced DNS
6. Add the records Vercel showed you
7. Wait 10–30 min for DNS to update
8. Your custom domain is live! ✅

---

## COSTS BREAKDOWN

| Item              | Cost              | Notes                          |
|-------------------|-------------------|--------------------------------|
| Vercel hosting    | FREE              | Up to 100GB bandwidth/month    |
| Anthropic API     | ~$0.003/message   | $10 = ~3,000 messages          |
| Custom domain     | ~$10–14/year      | Optional                       |
| SSL certificate   | FREE              | Auto by Vercel                 |
| **Total to start**| **~$20**          | API credit + optional domain   |

---

## WHAT HAPPENS WHEN USERS USE YOUR APP?

Every message a user sends costs you approximately:
- Short messages: ~$0.001–$0.003
- Long code generation: ~$0.01–$0.05

To protect yourself from high costs:
- Add a daily message limit per user (Step 9 below)
- Monitor usage at console.anthropic.com → Usage

---

## STEP 9 (OPTIONAL) — PROTECT FROM HIGH COSTS

Add this simple rate limiter to api/chat.js.
Replace the existing handler with the version that includes IP-based limiting.

Simple approach — add at top of api/chat.js:
```javascript
const DAILY_LIMIT = 20; // messages per IP per day
const ipLog = {}; // In production use Redis/Upstash instead

function checkLimit(ip) {
  const today = new Date().toDateString();
  const key = ip + '_' + today;
  ipLog[key] = (ipLog[key] || 0) + 1;
  return ipLog[key] <= DAILY_LIMIT;
}
```

Then in handler:
```javascript
const ip = req.headers['x-forwarded-for'] || req.connection.remoteAddress;
if (!checkLimit(ip)) {
  return res.status(429).json({ error: 'Daily limit reached. Try again tomorrow.' });
}
```

For production rate limiting, use Upstash Redis (free tier):
https://upstash.com

---

## NEXT UPGRADES (AFTER LAUNCH)

Once your app is live, here's what to add next:

### Week 1: Analytics
- Add Vercel Analytics (free): tracks visitors
- Dashboard: vercel.com → your project → Analytics

### Week 2: User Accounts (Supabase)
- Free tier: https://supabase.com
- Adds: email login, saved chats synced across devices
- Time: ~2 hours with a developer

### Week 3: Payments (Stripe)
- Free tier + Pro plan ($9–29/month)
- Website: https://stripe.com
- Time: ~4 hours with a developer or use Lemon Squeezy for simpler setup

### Month 2: Mobile App
- Wrap the HTML in a WebView using Capacitor (free)
- Submit to App Store + Google Play
- Guide: https://capacitorjs.com

---

## TROUBLESHOOTING

**"Cannot connect to server" error in the app**
→ Your API key isn't set in Vercel. Check Step 6.

**"HTTP 401" error**  
→ API key is wrong. Go to console.anthropic.com and create a new one.

**"HTTP 429" error**
→ You've hit Anthropic's rate limit. Add $10 more credit or wait an hour.

**App shows but AI doesn't respond**
→ Check Vercel function logs: vercel.com → project → Functions tab

**Custom domain not working**
→ DNS takes up to 48 hours. Check with: https://dnschecker.org

---

## GETTING HELP

- Vercel docs: https://vercel.com/docs
- Anthropic docs: https://docs.anthropic.com
- Community: https://discord.gg/anthropic

---

## QUICK REFERENCE COMMANDS

```bash
# Deploy to production
vercel --prod

# Check deployment logs
vercel logs

# List your deployments
vercel ls

# Open your project in browser
vercel open

# Pull environment variables locally
vercel env pull
```

---

You're now a founder. 🐙
Octopus AI is live. Ship it.
