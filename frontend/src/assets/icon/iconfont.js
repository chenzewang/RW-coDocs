!(function(t) {
  var e,
    n,
    c,
    o,
    i,
    l,
    d,
    a =
      '<svg><symbol id="icon-xiting" viewBox="0 0 3346 1024"><path d="M2206.619608 1024L3346.405229 271.058824l-39.822222-53.877125-1099.963399 726.169935L1139.785621 217.51634v-0.334641L0 970.457516l39.822222 53.542484L1139.785621 298.164706 2206.619608 1024z"  ></path><path d="M2226.028758 689.024837L3149.301961 53.542484 3109.479739 0 2186.206536 635.147712l39.822222 53.877125z"  ></path></symbol><symbol id="icon-juzhentanyuansujiegou" viewBox="0 0 1024 1024"><path d="M309.3 326.2l168.6-97.3c10 5.8 21.6 9.1 34 9.1 12.3 0 23.8-3.3 33.8-9L714 326.2c3.7-23.8 16.1-44.8 34-59.4L580.4 170v-0.5c0-37.8-30.7-68.5-68.5-68.5s-68.5 30.7-68.5 68.5v0.2l-168.2 97.1c17.9 14.6 30.4 35.6 34.1 59.4z" fill="#424242" ></path><path d="M842.9 624.2v-224c20.4-11.9 34.2-33.9 34.2-59.2 0-37.8-30.7-68.5-68.5-68.5-37.5 0-68.1 30.4-68.4 67.8L545.7 452.7c-10-5.7-21.5-9-33.8-9-12.4 0-24 3.4-34 9.1L283.1 340.4c-0.3-37.5-30.9-67.8-68.4-67.8-37.8 0-68.5 30.7-68.5 68.5 0 25.3 13.8 47.3 34.2 59.2v223.9c-20.4 11.9-34.2 33.9-34.2 59.2 0 37.8 30.7 68.5 68.5 68.5s68.5-30.7 68.5-68.5c0-25.3-13.8-47.3-34.2-59.2v-224c0.1-0.1 0.3-0.2 0.4-0.3L443.5 512v0.2c0 25.3 13.8 47.4 34.2 59.2v223.9c-20.4 11.9-34.2 33.9-34.2 59.2 0 37.8 30.7 68.5 68.5 68.5s68.5-30.7 68.5-68.5c0-25.3-13.8-47.3-34.2-59.2V571.4c20.4-11.8 34.2-33.9 34.2-59.2v-0.5L774 400c0.1 0.1 0.3 0.2 0.4 0.3v223.9c-20.4 11.9-34.2 33.9-34.2 59.2 0 37.8 30.7 68.5 68.5 68.5s68.5-30.7 68.5-68.5c-0.1-25.3-13.9-47.4-34.3-59.2z" fill="#424242" ></path><path d="M714 698.2l-141.9 81.9c18 14.6 30.5 35.5 34.3 59.3L748 757.6c-17.8-14.6-30.2-35.6-34-59.4zM451.5 780.2l-142.2-82.1c-3.7 23.8-16.1 44.8-34 59.4l142.1 82c3.7-23.7 16.1-44.6 34.1-59.3z" fill="#424242" ></path></symbol></svg>',
    s = (e = document.getElementsByTagName("script"))[
      e.length - 1
    ].getAttribute("data-injectcss");
  if (s && !t.__iconfont__svg__cssinject__) {
    t.__iconfont__svg__cssinject__ = !0;
    try {
      document.write(
        "<style>.svgfont {display: inline-block;width: 1em;height: 1em;fill: currentColor;vertical-align: -0.1em;font-size:16px;}</style>"
      );
    } catch (t) {
      console && console.log(t);
    }
  }
  function r() {
    l || ((l = !0), o());
  }
  (n = function() {
    var t,
      e,
      n,
      c,
      o,
      i = document.createElement("div");
    (i.innerHTML = a),
      (a = null),
      (t = i.getElementsByTagName("svg")[0]) &&
        (t.setAttribute("aria-hidden", "true"),
        (t.style.position = "absolute"),
        (t.style.width = 0),
        (t.style.height = 0),
        (t.style.overflow = "hidden"),
        (e = t),
        (n = document.body).firstChild
          ? ((c = e), (o = n.firstChild).parentNode.insertBefore(c, o))
          : n.appendChild(e));
  }),
    document.addEventListener
      ? ~["complete", "loaded", "interactive"].indexOf(document.readyState)
        ? setTimeout(n, 0)
        : ((c = function() {
            document.removeEventListener("DOMContentLoaded", c, !1), n();
          }),
          document.addEventListener("DOMContentLoaded", c, !1))
      : document.attachEvent &&
        ((o = n),
        (i = t.document),
        (l = !1),
        (d = function() {
          try {
            i.documentElement.doScroll("left");
          } catch (t) {
            return void setTimeout(d, 50);
          }
          r();
        })(),
        (i.onreadystatechange = function() {
          "complete" == i.readyState && ((i.onreadystatechange = null), r());
        }));
})(window);
