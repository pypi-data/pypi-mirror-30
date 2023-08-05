require.config({
  paths: {
    'clipboard': '++plone++permalink/clipboard.min'
  },
});

require([
  'jquery',
  'clipboard',
], function($, Clipboard){

  $(document).ready(function(){
    /* TODO:
       Make this based on a selection from controlpanel
    */
    var btns = [
      $('#plone-contentmenu-actions-permalink_with_clipboard'),
      $('#document-action-permalink_with_clipboard a'),
    ];
    btns.forEach(function(btn, index, array) {
      // Disable click on link
      btn.click(function(e) {
        e.preventDefault();
      });
      // Create Clipboard per button
      var clipboard = new Clipboard(btn.get(0), {
        text: function(trigger) {
          return trigger.getAttribute('href').split('?')[0];
        }
      });

      /*
        On success/error event write a portalmessage.
        TODO: find a better way to implement this.
        TODO: needs i18n.
      */
      clipboard.on('success', function(e){
        msg = $('<div class="portalMessage info"><strong>Info</strong>Permalink has been copied to clipboard.</div>');
        $('#global_statusmessage').append(msg);
      });
      clipboard.on('error', function(e){
        msg = $('<div class="portalMessage error"><strong>Error</strong>Couldn\'t copy Permalink to clipboard!</div>');
        $('#global_statusmessage').append(msg);
      });
    });
  });
});
