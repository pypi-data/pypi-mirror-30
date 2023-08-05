(function() {

  "use strict";

  window.onIframeLoaded = function(element) {
      $(element).prev().removeClass('loading');
  };

})();
