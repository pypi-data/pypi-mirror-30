$(window).on("load", function() {
    $(".ripiu-unite").each(function() {
      var confId = $(this).data("unite-conf");
      var conf = JSON.parse($("#" + confId).html());
      $(this).unitegallery(conf);
    });
});
