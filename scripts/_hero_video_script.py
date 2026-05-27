"""Inline <script> that drives the homepage video hero's fade.

Imported by generate_site_shell.py and used on the homepage and the
41 service-area pages so the same fade timing applies everywhere a
.home-hero-video element is present. Defined as a plain raw Python
string (not an f-string) so JS braces don't conflict with f-string
parsing.

The script is idempotent: it bails out if no .home-hero-video element
exists on the page, so including it on a page without the video hero
is harmless.
"""

HERO_VIDEO_SCRIPT = r"""<script>
(function () {
  var video = document.querySelector('.home-hero-video');
  if (!video) return;
  var FADE = 0.6;  // seconds at each end of the clip
  function setOpacity() {
    var t = video.currentTime;
    var d = video.duration;
    if (!d || !isFinite(d)) { video.style.opacity = '1'; return; }
    var op;
    if (t < FADE)              op = t / FADE;
    else if (t > d - FADE)     op = (d - t) / FADE;
    else                       op = 1;
    if (op < 0) op = 0; else if (op > 1) op = 1;
    video.style.opacity = String(op);
  }
  function tick() {
    setOpacity();
    requestAnimationFrame(tick);
  }
  // Kick off — autoplay attribute should start it, but defensively
  // call play() in case the browser deferred it (Safari sometimes does).
  var p = video.play();
  if (p && typeof p.catch === 'function') p.catch(function () { /* autoplay blocked; ignore */ });
  requestAnimationFrame(tick);
})();
</script>"""
