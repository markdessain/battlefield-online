$( document ).ready(function() {
  $.ajax({
      url: '/graph',
      type: 'GET',
      success: function(data) {
        console.log(data.labels.length);
        console.log(data.datasets.created_at_hour.length);
        var ctx = document.getElementById("tweet_chart");
        var myChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [
                  {
                      label: '# of Retweets',
                      data: data.datasets.retweets_at_hour,
                      backgroundColor: 'rgba(255,99,132,0.2)',
                      borderColor: 'rgba(255,99,132,1)',
                      borderWidth: 1,
                  },
                  {
                      label: '# of Tweets',
                      data: data.datasets.created_at_hour,
                      backgroundColor: 'rgba(54, 162, 235, 0.2)',
                      borderColor: 'rgba(54, 162, 235, 1)',
                      borderWidth: 1,
                  }
                ]
            },
            options: {
                scales: {
                    yAxes: [{
                        ticks: {
                            beginAtZero:true
                        }
                    }]
                }
            }
        });
      }
  });

  $.ajax({
      url: '/top',
      type: 'GET',
      success: function(data) {
        $.each(data.media, function() {
            $('#media').append('<img src="' + this + '"/>');
        });

        $.each(data.hashtags, function() {
            $('#hashtags').append('<li><a href="https://twitter.com/hashtag/' + this + '">#' + this + '</a></li>');
        });

        $.each(data.user_mentions, function() {
            $('#user_mentions').append('<li><a href="https://twitter.com/' + this + '"><img src="https://twitter.com/' + this + '/profile_image?size=bigger" /></a></li>');
        });



        function collage() {
            $('#media').removeWhitespace().collagePlus({
              'fadeSpeed'       : "slow",
            });
        };


        var resizeTimer = null;
        $(window).bind('resize', function() {
            // hide all the images until we resize them
            // set the element you are scaling i.e. the first child nodes of ```.Collage``` to opacity 0
            $('#media .Image_Wrapper').css("opacity", 0);
            // set a timer to re-apply the plugin
            if (resizeTimer) clearTimeout(resizeTimer);
            resizeTimer = setTimeout(collage, 200);
        });

        collage();

      }
  });

});
