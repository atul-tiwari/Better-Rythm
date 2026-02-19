# Deploy Better Rythm Discord Bot on Ubuntu Server

Step-by-step guide to deploy the Discord music bot on an Ubuntu server using Docker.

---

## Prerequisites

- **Ubuntu Server** (20.04 LTS or 22.04 LTS recommended)
- **SSH access** to the server
- **Discord Bot Token** and **YouTube API Key** (see Step 1)
- **Docker** and **Docker Compose** (installed in Step 2)

---

## Step 1: Get Discord Token and YouTube API Key (Do this on your PC)

### 1.1 Discord Bot Token

1. Go to [Discord Developer Portal](https://discord.com/developers/applications).
2. Click **New Application** and give it a name (e.g. "Better Rythm Bot").
3. In the left sidebar, open **Bot**.
4. Click **Add Bot**.
5. Under **Token**, click **Reset Token** or **Copy** and **save the token** somewhere safe (you won’t see it again).
6. Enable **Message Content Intent**:
   - Open **Bot** → **Privileged Gateway Intents**.
   - Turn **ON**: **Message Content Intent**.
   - Click **Save Changes**.
7. Invite the bot to your server:
   - Open **OAuth2** → **URL Generator**.
   - **Scopes**: check **bot**.
   - **Bot Permissions**: check **Connect**, **Speak**, **Use Voice Activity**, **Send Messages**, **Embed Links**, **Read Message History**, **Add Reactions**, **Use Slash Commands** (or “Administrator” for testing).
   - Copy the generated URL, open it in a browser, choose your server, and authorize.

### 1.2 YouTube API Key

1. Go to [Google Cloud Console](https://console.developers.google.com/).
2. Create a project (or select one): **Select a project** → **New Project** → name it → **Create**.
3. Enable **YouTube Data API v3**:
   - **APIs & Services** → **Library** → search **YouTube Data API v3** → **Enable**.
4. Create an API key:
   - **APIs & Services** → **Credentials** → **Create Credentials** → **API Key**.
   - Copy the key and (optional) restrict it to **YouTube Data API v3** and by IP if you want.

Keep both **Discord Token** and **YouTube API Key** ready for Step 5.

---

## Step 2: Prepare the Ubuntu Server

### 2.1 Connect via SSH

```bash
ssh your_username@your_server_ip
```

Replace `your_username` and `your_server_ip` with your SSH user and server IP.

### 2.2 Update the system

```bash
sudo apt update && sudo apt upgrade -y
```

### 2.3 Install Docker

```bash
# Install Docker
sudo apt install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### 2.4 Allow your user to run Docker (optional, avoids typing `sudo` for docker)

```bash
sudo usermod -aG docker $USER
```

Then **log out and log back in** (or run `newgrp docker`) so the group change applies.

### 2.5 Verify Docker

```bash
docker --version
docker compose version
```

You should see Docker and Docker Compose (v2) versions.

---

## Step 3: Clone the Project

### 3.1 Choose a directory and clone

Example: clone into `~/better-rythm-discord`:

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git better-rythm-discord
cd better-rythm-discord
```

Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` with your GitHub (or GitLab) username and repo name.  
If you use **SSH**:

```bash
git clone git@github.com:YOUR_USERNAME/YOUR_REPO_NAME.git better-rythm-discord
cd better-rythm-discord
```

---

## Step 4: Create `queue.json` (so the queue persists)

The bot reads and writes the queue to `queue.json`. Create an empty queue file:

```bash
echo '[]' > queue.json
```

Optional: make it writable by everyone (Docker may run as a different user):

```bash
chmod 666 queue.json
```

---

## Step 5: Configure Environment Variables

### 5.1 Copy the example env file

```bash
cp .env.example .env
```

### 5.2 Edit `.env` with your values

```bash
nano .env
```

Set at least these (use the token and API key from Step 1):

```env
# Required
DISCORD_TOKEN=your_actual_discord_bot_token_here
YOUTUBE_API_KEY=your_actual_youtube_api_key_here

# Optional
DISCORD_GUILD_ID=0
MAX_QUEUE_SIZE=50
MAX_SONG_DURATION=600
DEFAULT_VOLUME=0.5
```

- **DISCORD_TOKEN**: Paste the Discord bot token from Step 1.1.  
- **YOUTUBE_API_KEY**: Paste the YouTube API key from Step 1.2.  
- **DISCORD_GUILD_ID**: `0` = all servers; or set your server’s ID for single-server use.  
- Leave **FFMPEG_LOCATION** commented out (Docker image already has ffmpeg).

Save and exit: **Ctrl+O**, **Enter**, **Ctrl+X**.

### 5.3 Restrict permissions on `.env` (recommended)

```bash
chmod 600 .env
```

---

## Step 6: Build and Run with Docker Compose

### 6.1 Build the image and start the container

From the project directory (`better-rythm-discord`):

```bash
docker compose up -d --build
```

- `--build`: build the image from the Dockerfile.  
- `-d`: run in the background.

### 6.2 Check that the container is running

```bash
docker compose ps
```

You should see `better-rythm-discord-bot` with status **Up**.

### 6.3 View logs (to confirm the bot connected)

```bash
docker compose logs -f
```

You should see something like:

- `Starting Discord Music Bot...`
- `Bot will be available in Discord!`
- `YourBotName has connected to Discord!`

Press **Ctrl+C** to stop following logs (the container keeps running).

---

## Step 7: Verify in Discord

1. Open your Discord server where you invited the bot.
2. In a text channel, type: `!help_music`
3. The bot should reply with the command list.
4. Join a voice channel and run: `!play song name`
5. The bot should join and start playing (or add to queue).

If it doesn’t respond, check logs (Step 6.3) and ensure **Message Content Intent** is enabled (Step 1.1).

---

## Step 8: Useful Commands After Deployment

Run these from the project directory (`~/better-rythm-discord`).

| Task              | Command                          |
|-------------------|----------------------------------|
| View logs         | `docker compose logs -f`         |
| Stop the bot      | `docker compose down`             |
| Start again       | `docker compose up -d`           |
| Restart           | `docker compose restart`         |
| Rebuild and start | `docker compose up -d --build`    |
| Container status  | `docker compose ps`              |

The `restart: unless-stopped` setting in `docker-compose.yml` makes the bot start again after a server reboot.

---

## Troubleshooting

### Bot doesn’t respond to commands

- Confirm **Message Content Intent** is ON in Discord Developer Portal → Bot → Privileged Gateway Intents.
- Check logs: `docker compose logs -f` for errors.

### “Failed to load audio” or no sound

- FFmpeg is inside the container; you usually don’t need `FFMPEG_LOCATION`.
- If you see YouTube errors, check your **YouTube API key** and quota in Google Cloud Console.

### Container exits immediately

- Check logs: `docker compose logs`.
- Ensure `.env` has valid `DISCORD_TOKEN` and `YOUTUBE_API_KEY` (no extra spaces or quotes unless required).
- Ensure `queue.json` exists: `ls -la queue.json` and that it contains `[]`.

### Permission denied on `queue.json`

From the project directory:

```bash
sudo chown 1000:1000 queue.json
chmod 664 queue.json
```

Then:

```bash
docker compose restart
```

(If your Docker runs the app as a different user, adjust the UID/GID; `1000` is often the first non-root user in the image.)

### “Cannot connect to Docker daemon”

- Either run Docker commands with `sudo` (e.g. `sudo docker compose up -d`), or add your user to the `docker` group (Step 2.4) and log out and back in.

---

## Summary Checklist

- [ ] Discord bot created; token copied; Message Content Intent enabled; bot invited to server.
- [ ] YouTube Data API v3 enabled; API key created and copied.
- [ ] Ubuntu server updated; Docker and Docker Compose installed.
- [ ] Project cloned; `cd` into project directory.
- [ ] `queue.json` created with `echo '[]' > queue.json`.
- [ ] `.env` created from `.env.example` and filled with Discord token and YouTube API key.
- [ ] `docker compose up -d --build` run successfully.
- [ ] `docker compose logs -f` shows bot connected.
- [ ] In Discord, `!help_music` and `!play` work.

Once all steps are done, your Better Rythm Discord bot is deployed on Ubuntu and will keep running (and restart after reboots) until you run `docker compose down`.
