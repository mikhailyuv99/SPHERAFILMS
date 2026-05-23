/**
 * Detect in-app browsers (Instagram, Facebook, etc.) — fixed background + no Lenis
 */
(function () {
  const ua = navigator.userAgent || "";
  if (
    /Instagram|FBAN|FBAV|FB_IAB|Twitter|Line\/|Snapchat|LinkedInApp|TikTok|MicroMessenger|WhatsApp/i.test(
      ua
    )
  ) {
    document.documentElement.classList.add("is-inapp");
  }
})();
