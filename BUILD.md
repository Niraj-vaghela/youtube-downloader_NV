# How to Build the Android APK

Since setting up an Android Build Environment on Windows is complex (requires Android Studio, SDK, NDK, Flutter, etc.), the easiest way to build your APK is using **GitHub Actions**. I have already set up the workflow file for you.

## Step 1: Create a GitHub Repository
1. Go to [github.com/new](https://github.com/new).
2. Name your repository (e.g., `youtube-downloader-app`).
3. Create it (Public or Private doesn't matter).

## Step 2: Push Your Code
Run these commands in your terminal (inside this folder):

```bash
# Initialize git if not done
git init
git add .
git commit -m "Initial commit of Downloader App"

# Link to your new repo (replace URL with yours)
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/youtube-downloader-app.git
git push -u origin main
```

## Step 3: Wait for Build
1. Go to your repository on GitHub.
2. Click the **Actions** tab.
3. You will see a workflow named "Build Android APK" running.
4. Wait for it to turn Green (Success). It usually takes 3-5 minutes.

## Step 4: Download APK
1. Click on the completed "Build Android APK" run.
2. Scroll down to the **Artifacts** section.
3. Click on **youtube-downloader-apk** to download the zip file.
4. Extract the zip, transfer the `.apk` file to your phone, and install it!

> **Note**: Since this is a self-signed debug/release build, your phone might ask for permission to "Install from Unknown Sources". This is normal for testing.
