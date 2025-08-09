# Security Deployment Guide

## API Key Protection Checklist

### ✅ Implemented Protections

1. **Rate Limiting**
   - 5 analyses per hour for demo users
   - Usage counter display
   - Automatic hourly reset

2. **Input Validation**
   - Text length limits (50,000 chars)
   - Content validation
   - Prompt injection detection

### 🔒 OpenAI Account Setup

1. **Set Usage Limits**
   ```
   OpenAI Dashboard → Usage → Limits
   Monthly Budget: $20-50
   Email Alerts: 50%, 80%, 90%
   Hard Limit: Enabled
   ```

2. **API Key Management**
   - Use restricted API keys if available
   - Set up separate keys for dev/prod
   - Monitor usage regularly

### 🚀 Deployment Configuration

#### Streamlit Cloud
```toml
# Secrets (not in code!)
OPENAI_API_KEY = "sk-your-key-here"
DEMO_MODE = "true"
```

#### Heroku/Railway
```bash
heroku config:set OPENAI_API_KEY=sk-your-key
heroku config:set DEMO_MODE=true
```

### 📊 Monitoring & Alerts

1. **OpenAI Dashboard**: Check usage daily
2. **Cost Alerts**: Set up email notifications
3. **Application Logs**: Monitor for unusual patterns

### 🛡️ Additional Security Measures

#### For Production Apps:
- User authentication (Auth0, Firebase)
- IP-based rate limiting
- CAPTCHA for high usage
- Webhook monitoring
- Database logging of all requests

#### For Public Demos:
- Clear usage disclaimers
- "Demo only" messaging
- Limited functionality warnings
- Contact information for abuse reports

### 🚨 Incident Response

If you notice unusual usage:

1. **Immediate**: Disable/rotate API key
2. **Check**: OpenAI usage dashboard
3. **Review**: Application logs
4. **Update**: Rate limits if needed
5. **Monitor**: Closely for 24-48 hours

### 💡 Alternative Approaches

#### Option 1: Static Demo
- Pre-generate analysis results
- No live API calls
- Zero API costs
- Limited interactivity

#### Option 2: Freemium Model
- Free tier: 2-3 analyses
- Paid tier: Unlimited usage
- User accounts required
- Payment processing

#### Option 3: Waitlist/Access Codes
- Controlled user access
- Manual approval process
- Higher usage limits for approved users
- Better cost control

### 📞 Support Information

**If you experience issues:**
- Monitor OpenAI usage at: https://platform.openai.com/usage
- Check application logs
- Review rate limiting settings
- Contact for security concerns

**Remember**: The goal is to showcase your skills while protecting your costs!
