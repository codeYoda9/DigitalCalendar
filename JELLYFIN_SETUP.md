Jellyfin setup notes
====================

Prerequisites (host)
- Install Intel VA-API drivers (e.g., `libva2`, `intel-media-driver` or `i965-va-driver`) so `/dev/dri` is available.
- Docker and Docker Compose installed and usable by your user.

Start the stack

1. (Optional) If you plan to use a domain, add a Caddy site for your domain in `Caddyfile` pointing to `jellyfin:8096`.
2. Start the services:

```bash
docker-compose up -d jellyfin caddy
```

3. If you exposed port 8096, open `http://HOST:8096` or use your domain with HTTPS via Caddy.

Verify VA-API availability

1. Check container logs for VA-API detection:

```bash
docker-compose logs -f jellyfin
```

2. Look for lines indicating VA-API/Intel QuickSync usage during playback/transcoding.

Backups

- Use the helper script to backup the Jellyfin config volume to `./backups`:

```bash
./scripts/backup_jellyfin.sh ./backups
```

Notes
- If you prefer bind-mounting host media, replace the `jellyfin_media` volume with a host path in `docker-compose.yaml`.
- For production public exposure, obtain a proper domain (or use DuckDNS) and enable the Caddy site entry to get automatic TLS.
