// Reload the page every minute, but only if it can be fetched: a failed
// reload shows the browser's error page, which never refreshes again.
setInterval(() => {
  // Pages opened from disk cannot be fetched, the page is always replaced
  // atomically, so reloading is safe
  if (location.protocol === "file:") {
    location.reload();
    return;
  }

  fetch(location.href, { method: "HEAD", cache: "no-store" })
    .then((response) => {
      if (response.ok) {
        location.reload();
      }
    })
    .catch(() => {});
}, 60000);
