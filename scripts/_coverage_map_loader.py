"""Inline <script> loader for the Leaflet-based coverage map.

Imported by both markdown_to_html.py and generate_site_shell.py so the
JS lives in exactly one place. Defined as a plain Python string
(not an f-string) so the JS braces don't conflict with f-string parsing.
"""

COVERAGE_MAP_LOADER = r"""<script>
/* Coverage-map loader. Only injects Leaflet (CSS + JS) when a
   .coverage-map element exists on the page. Reads data-* attributes
   off each map element and renders the appropriate variant. */
(function () {
  var maps = document.querySelectorAll('.coverage-map');
  if (!maps.length) return;

  var WATERLOO = [42.51389, -92.34611];

  function inject(tag, attrs) {
    var el = document.createElement(tag);
    for (var k in attrs) el.setAttribute(k, attrs[k]);
    return el;
  }
  function loadLeaflet(cb) {
    if (window.L) { cb(); return; }
    document.head.appendChild(inject('link', {
      rel: 'stylesheet',
      href: 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',
      integrity: 'sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=',
      crossorigin: ''
    }));
    var s = inject('script', {
      src: 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',
      integrity: 'sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=',
      crossorigin: ''
    });
    s.onload = cb;
    document.body.appendChild(s);
  }

  function tileLayer() {
    return L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 18,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    });
  }
  function originIcon() {
    return L.divIcon({
      className: 'coverage-map-origin',
      html: '<div style="background:#b8341a;color:#fff;border:2px solid #fff;border-radius:50%;width:24px;height:24px;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:13px;box-shadow:0 2px 6px rgba(0,0,0,0.35);">&#9733;</div>',
      iconSize: [24, 24],
      iconAnchor: [12, 12]
    });
  }
  function cityIcon() {
    return L.divIcon({
      className: 'coverage-map-city',
      html: '<div style="background:#fff;border:2px solid #b8341a;border-radius:50%;width:14px;height:14px;box-shadow:0 1px 3px rgba(0,0,0,0.3);"></div>',
      iconSize: [14, 14],
      iconAnchor: [7, 7]
    });
  }

  function renderCity(el) {
    var coords = JSON.parse(el.getAttribute('data-coords') || 'null');
    if (!coords) return;
    var cityName = el.getAttribute('data-city') || '';
    var distance = el.getAttribute('data-distance') || '';
    var map = L.map(el, { zoomControl: true, scrollWheelZoom: false }).setView(coords, 7);
    tileLayer().addTo(map);
    L.marker(WATERLOO, { icon: originIcon() }).addTo(map)
      .bindPopup('<strong>Waterloo, IA</strong><br>Midwest CNC Services');
    L.marker(coords, { icon: cityIcon() }).addTo(map)
      .bindPopup('<strong>' + cityName + '</strong>' + (distance ? '<br>' + distance + ' from Waterloo' : ''));
    L.polyline([WATERLOO, coords], { color: '#b8341a', weight: 2, dashArray: '6,6', opacity: 0.6 }).addTo(map);
    map.fitBounds([WATERLOO, coords], { padding: [50, 50] });
    el.classList.add('is-loaded');
  }
  function renderState(el) {
    var bounds = JSON.parse(el.getAttribute('data-bounds') || 'null');
    var cities = JSON.parse(el.getAttribute('data-cities') || '[]');
    var map = L.map(el, { zoomControl: true, scrollWheelZoom: false });
    tileLayer().addTo(map);
    L.marker(WATERLOO, { icon: originIcon() }).addTo(map)
      .bindPopup('<strong>Waterloo, IA</strong><br>Midwest CNC Services');
    var allPts = [WATERLOO];
    cities.forEach(function (c) {
      if (!c.coords) return;
      L.marker(c.coords, { icon: cityIcon() }).addTo(map)
        .bindPopup('<strong>' + c.name + '</strong>' +
                   (c.distance_miles ? '<br>' + c.distance_miles + ' miles from Waterloo' : '') +
                   (c.url ? '<br><a href="' + c.url + '">View ' + c.name + ' page &rarr;</a>' : ''));
      allPts.push(c.coords);
    });
    if (bounds && bounds.length === 2) {
      map.fitBounds(bounds, { padding: [30, 30] });
    } else if (allPts.length > 1) {
      map.fitBounds(allPts, { padding: [40, 40] });
    }
    el.classList.add('is-loaded');
  }
  function renderHub(el) {
    var cities = JSON.parse(el.getAttribute('data-cities') || '[]');
    var map = L.map(el, { zoomControl: true, scrollWheelZoom: false });
    tileLayer().addTo(map);
    L.marker(WATERLOO, { icon: originIcon() }).addTo(map)
      .bindPopup('<strong>Waterloo, IA</strong><br>Midwest CNC Services<br>Service across 7 states');
    var allPts = [WATERLOO];
    cities.forEach(function (c) {
      if (!c.coords) return;
      L.marker(c.coords, { icon: cityIcon() }).addTo(map)
        .bindPopup('<strong>' + c.name + ', ' + (c.state || '') + '</strong>' +
                   (c.distance_miles ? '<br>' + c.distance_miles + ' miles from Waterloo' : '') +
                   (c.url ? '<br><a href="' + c.url + '">View ' + c.name + ' page &rarr;</a>' : ''));
      allPts.push(c.coords);
    });
    if (allPts.length > 1) map.fitBounds(allPts, { padding: [30, 30] });
    el.classList.add('is-loaded');
  }

  loadLeaflet(function () {
    maps.forEach(function (el) {
      if (el.classList.contains('coverage-map--city'))      renderCity(el);
      else if (el.classList.contains('coverage-map--hub'))  renderHub(el);
      else                                                  renderState(el);
    });
  });
})();
</script>"""
