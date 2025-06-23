# Academic Chatbot - Deployment Guide

## 🚀 Features

- **Modern Chat UI** dengan desain mirip ChatGPT/Claude
- **Firebase Authentication** untuk login/register user
- **Firestore Database** untuk menyimpan riwayat chat
- **Admin Panel** dengan export data dan analytics
- **Pagination** untuk riwayat chat yang panjang
- **Typing Indicator** saat menunggu response
- **Responsive Design** dengan tema biru langit
- **Integration** dengan Llama 3.1 fine-tuned model via ngrok

## 📋 Prerequisites

1. **Firebase Project** dengan Firestore enabled
2. **Service Account Key** dari Firebase
3. **Ngrok API endpoint** yang running
4. **Python 3.8+**

## 🔧 Local Development Setup

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd academic-chatbot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Firebase Setup

1. Buat project di [Firebase Console](https://console.firebase.google.com/)
2. Enable **Firestore Database** dan **Authentication**
3. Generate **Service Account Key**:
   - Go to Project Settings > Service Accounts
   - Click "Generate new private key"
   - Download JSON file
4. Rename file menjadi `firebase-credentials.json` dan letakkan di root folder

### 4. Configure Admin Users

Edit `main.py` line 110 untuk menambah admin emails:

```python
admin_emails = ["admin@akademik.com", "your-admin@email.com"]
```

### 5. Update API URL

Edit `main.py` atau gunakan environment variable untuk ngrok URL:

```python
self.api_url = "https://your-ngrok-url.ngrok.io"
```

### 6. Run Application

```bash
streamlit run main.py
```

## ☁️ Streamlit Cloud Deployment

### 1. GitHub Setup

1. Push code ke GitHub repository
2. Pastikan `firebase-credentials.json` **TIDAK** di-commit (add ke `.gitignore`)

### 2. Streamlit Cloud Configuration

1. Connect repository di [Streamlit Cloud](https://share.streamlit.io/)
2. Set main file path: `main.py`
3. Configure secrets di Streamlit Cloud dashboard

### 3. Secrets Configuration

Di Streamlit Cloud > App Settings > Secrets, tambahkan:

```toml
# Ngrok API URL
ngrok_api_url = "https://your-ngrok-url.ngrok.io"

# Firebase Configuration
[firebase]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYour-Private-Key-Content\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project-id.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project-id.iam.gserviceaccount.com"
```

### 4. Deploy

Streamlit Cloud akan auto-deploy setelah secrets dikonfigurasi.

## 🔐 Security Notes

### Firebase Rules

Set Firestore rules untuk security:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can only access their own conversations
    match /conversations/{userId}/messages/{messageId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }

    // Admin can read all (implement admin check in your app)
    match /conversations/{userId}/messages/{messageId} {
      allow read: if request.auth != null &&
        request.auth.token.email in ['admin@akademik.com'];
    }
  }
}
```

### Environment Variables

Untuk production, gunakan environment variables:

```bash
export NGROK_API_URL="https://your-ngrok-url.ngrok.io"
export FIREBASE_PROJECT_ID="your-project-id"
```

## 📊 API Format

### Request Format

```json
POST /generate
Content-Type: application/json

{
  "prompt": "User question here"
}
```

### Response Format

```json
{
  "response": "AI response here",
  "status": "success"
}
```

### Error Response

```json
{
  "error": "Error message",
  "status": "error"
}
```

## 🎨 Customization

### Mengubah Tema Warna

Edit CSS variables di `main.py`:

```css
:root {
  --primary-color: #87ceeb; /* Sky Blue */
  --secondary-color: #4682b4; /* Steel Blue */
  --accent-color: #1e90ff; /* Dodger Blue */
}
```

### Menambah Logo Custom

Replace Google logo URL di `render_chat_header()`:

```html
<img src="your-logo-url.png" width="60" height="20" alt="Logo" />
```

### Mengubah Admin Emails

Edit list admin di `AuthManager.is_admin()`:

```python
admin_emails = ["admin@akademik.com", "superadmin@akademik.com"]
```

## 🔧 Troubleshooting

### Common Issues

1. **Firebase Connection Error**

   - Pastikan service account key valid
   - Check project ID dan permissions
   - Verify Firestore rules

2. **API Connection Error**

   - Pastikan ngrok tunnel aktif
   - Check API endpoint URL
   - Verify API response format

3. **Authentication Issues**

   - Enable Email/Password authentication di Firebase
   - Check admin email configuration
   - Verify Firebase Auth rules

4. **Deployment Issues**
   - Check Streamlit Cloud secrets format
   - Verify all dependencies di requirements.txt
   - Check Python version compatibility

### Debug Mode

Untuk debugging, tambahkan logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Performance Tips

1. **Firestore Optimization**

   - Use pagination untuk data besar
   - Create indexes untuk queries
   - Limit message history

2. **API Optimization**

   - Implement caching untuk frequent queries
   - Add timeout handling
   - Use connection pooling

3. **UI/UX**
   - Lazy load chat history
   - Optimize CSS animations
   - Compress images/assets

## 🆘 Support

Jika ada masalah:

1. Check logs di Streamlit Cloud dashboard
2. Verify Firebase console untuk errors
3. Test API endpoint manually
4. Check GitHub Issues untuk known problems

## 📝 License

MIT License - Feel free to modify and use for your projects!
