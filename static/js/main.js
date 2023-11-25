$(document).ready(function () {
  $(".editmember").on("click", function () {
    $("#informationUser").removeClass("hidden");
  });
  $("#closeButton").on("click", function () {
    $("#informationUser").addClass("hidden");
  });

  $("#buttonloginAdmin").on("click", function () {
    $("#loginAdmin").removeClass("hidden");
  });
  $("#closeButtonAdmin").on("click", function () {
    $("#loginAdmin").addClass("hidden");
  });

  $("#closeButtonSearch").click(function () {
    $("#searchResults").animate({ right: -350 }, 350, function () {
      $(this).removeClass("no-overlay");
      $(this).hide();
    });
    $(".overlay").remove();
  });
  $("#performSearch").click(function () {
    // Xử lý tìm kiếm ở đây
    var searchQuery = $("#searchInput").val();
    // Gửi dữ liệu tìm kiếm đến máy chủ (ví dụ bằng AJAX) và hiển thị kết quả tại #searchOutput
  });

  const body = $("body");
  const imgdarklight = $("#imgdarklight");
  $(document).on("click", ".dark-light", function () {
    if (body.hasClass("dark-mode")) {
      imgdarklight.attr("src", "/static/img/icon/sunny.png");
      body.removeClass("dark-mode");
      body.addClass("light-mode");
    } else {
      imgdarklight.attr("src", "/static/img/icon/dark.png");
      body.removeClass("light-mode");
      body.addClass("dark-mode");
    }
  });
  $(document).on("click", ".js-show-modal1", function (e) {
    e.preventDefault();
    $(".js-modal1").removeClass("hidden");
  });

  $(document).on("click", ".js-hide-modal1", function () {
    $(".js-modal1").addClass("hidden");
  });
});
