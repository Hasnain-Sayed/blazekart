# 🛒 BlazeKart
### A Full-Stack Django E-Commerce Platform

BlazeKart is a modern, production-ready e-commerce web application built with Django 5. It features a complete shopping experience — from browsing and wishlisting to checkout, order tracking, and two-factor authentication — all backed by secure, environment-based configuration.

---

## 🚀 Features at a Glance

### 👤 Authentication & Security
- Custom User Model with email-based verification
- Password reset via email
- Two-Factor Authentication (TOTP)
- Secure environment-based settings via `.env`

### 🛍️ Store & Products
- Product listing with dynamic category filtering and search
- Product detail pages with variations (size, color), stock handling, and a review system

### 🛒 Cart System
- Guest cart with session-based merging on login
- Quantity updates and a global cart context processor

### ❤️ Wishlist
- Add/remove products from wishlist
- Accessible from the user dashboard

### 💳 Orders & Checkout
- Full checkout workflow with order creation and payment handling
- Order confirmation emails, status updates, history, and detail pages

### 📊 User Dashboard
- Profile, address, and billing management
- Overview of recent orders, cart, wishlist, payment methods, and 2FA settings

### ✉️ Email System
- Transactional emails for account activation, password reset, and order confirmation
- Configured with secure SMTP and environment-variable-protected credentials

---

## 🛠 Tech Stack

| Layer        | Technology                    |
|--------------|-------------------------------|
| Backend      | Django 5                      |
| Frontend     | HTML, CSS, Bootstrap          |
| Database     | SQLite (Development)          |
| Auth         | Django Auth + Custom Model    |
| 2FA          | Django OTP (TOTP)             |
| Email        | SMTP (App Password based)     |
| Version Control | Git & GitHub               |

---

## 📂 Project Structure

```
blazekart/
│
├── accounts/        # Authentication & user management
├── cart/            # Cart logic & utilities
├── category/        # Product categories
├── dashboard/       # User dashboard & profile
├── orders/          # Checkout & order processing
├── store/           # Product models & views
├── templates/       # HTML templates
├── static/          # CSS, JS, Images
├── manage.py
└── settings.py
```

## 🔐 Security Notes

- All secrets are loaded from environment variables — never hardcoded
- TOTP-based 2FA is available for all user accounts
- Email verification is required before account activation
- Password reset flow uses time-limited, signed tokens

---

## 📬 Contact & Support

If you discover any issues or have suggestions for improvement, please open an Issue on this repository. Feedback and contributions are highly appreciated.

---


👨‍💻 Author

Hasnain Sayed
Full Stack Developer
Creator of BlazeKart

⭐ If You Like This Project

Give it a star ⭐
Fork it 🍴
Build on it 🚀

> Built with ❤️ using Django 5 · Demonstrates full-stack development across auth, e-commerce logic, email integration, and secure configuration.
