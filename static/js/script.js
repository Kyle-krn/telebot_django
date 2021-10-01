$(window).scroll(function() {
    if ($(document).scrollTop() > 600 && $("#myModal").attr("displayed") === "false") {
      $('#myModal').modal('show');
      $("#myModal").attr("displayed", "true");
    }
  });