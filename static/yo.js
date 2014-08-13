google.setOnLoadCallback(function() {
  $(document).ready(function() {
    
    // Define some variables used to remember state.
    var playlistId, channelId;

    // Create a private playlist.
    function addThumbnails() {
      gapi.client.setApiKey('AIzaSyBU9eMQ1xW0NNEGprJIR5wgaQdrTFn_Fdc');

      gapi.client.load('youtube', 'v3', function() {

        $('.yotuber').each(function() {
          var self = $(this),
              username = self.data('username');

          var request = gapi.client.youtube.channels.list({
            part: 'snippet',
            forUsername: username
          });

          request.execute(function(response) {
            console.log(response);
            var result = response.result;
            if (result) {
              photo = result.items[0].snippet.thumbnails.default.url;
              self.find('img').attr('src', photo);
            } 
          });
        });

      });
    }

    addThumbnails();
  });
});