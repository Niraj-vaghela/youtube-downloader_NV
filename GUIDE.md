# User Guide: Build & Publish

## Part 1: How to Build the APK (Step-by-Step)

We are using **GitHub Actions** to build the App. This means GitHub's computers will do the heavy lifting.

### 1. Create a GitHub Account & Repository
1.  Log in to [GitHub](https://github.com).
2.  Click the **+** icon (top right) -> **New repository**.
3.  Name it `youtube-downloader` and click **Create repository**.

### 2. Push Your Code
Open your terminal (Command Prompt or PowerShell) in this project folder and run these commands one by one:

```bash
# 1. Initialize Git
git init

# 2. Add all files
git add .

# 3. Commit (Save) files
git commit -m "Initial version"

# 4. Link to your GitHub Repo
# REPLACE THE URL BELOW with your actual repository URL
git remote add origin https://github.com/YOUR_USERNAME/youtube-downloader.git

# 5. Upload Code
git branch -M main
git push -u origin main
```

### 3. Download the APK
1.  Go to your repository page on GitHub.
2.  Click the **Actions** tab at the top.
3.  You will see a workflow running (yellow circle). Wait for it to turn green (3-5 mins).
4.  Click on the workflow name.
5.  Scroll down to **Artifacts** and click **youtube-downloader-apk** to download it.

---

## Part 2: Publishing to Google Play Store

> **⚠️ CRITICAL WARNING**: Google generally **bans** YouTube Downloaders from the Play Store because they violate YouTube's Terms of Service. If you publish this app, your developer account could be **banned**.
> 
> *Alternative*: You can distribute the APK directly via a website, Telegram, or alternative stores like F-Droid or Aptoide.

If you still wish to proceed (or publish a different app later), here are the steps:

### 1. Google Play Console Account
-   Go to [Google Play Console](https://play.google.com/console).
-   Pay the one-time **$25 registration fee**.
-   Verify your identity.

### 2. Build a Signed App Bundle (AAB)
The Play Store requires an **AAB** file, not an APK, and it must be **Signed** with a Keystore.
To do this via GitHub Actions requires extra setup:
1.  Generate a keystore file locally (`keytool -genkey ...`).
2.  Upload the keystore to GitHub Secrets.
3.  Update the `build_apk.yaml` to sign the app.

### 3. Create Store Listing
In the Console:
-   **Main Store Listing**: Upload App Icon (512x512), Feature Graphic (1024x500), and Screenshots.
-   **Description**: Write a Title and Description.
-   **Privacy Policy**: You must host a Privacy Policy URL explaining what user data you collect (even if none).

### 4. Release
-   Upload your `.aab` file to the "Production" track.
-   Submit for review. Google takes 1-7 days to review.

**Note**: For this specific YouTube Downloader app, I highly recommend **Part 1 (Direct APK distribution)** to avoid account bans.
