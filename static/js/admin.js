$(document).ready(function () {
  $("#remove").click(function () {
    $("#confirmdelete").addClass("hidden");
    $(".close_confirm").addClass("hidden");
  });
  $("#cancel").click(function () {
    $("#confirmdelete").addClass("hidden");
    $(".close_confirm").addClass("hidden");
  });
  $(".close_confirm").click(function () {
    $("#confirmdelete").addClass("hidden");
    $(".close_confirm").addClass("hidden");
  });
  $(".searchButton").click(function () {
    // Khi người dùng click vào nút tìm kiếm
    $("#searchResults").show().animate({ right: 0 }, 250); // Di chuyển về vị trí hiển thị

    $("<div class='overlay'></div>").appendTo("body");
    $("#searchResults").addClass("no-overlay");
  });
  $(document).on("click", ".collapsible", function () {
    $(".collapsible").removeClass("active");

    $(this).toggleClass("active");

    var content = $(this).next();

    if (content.is(":visible")) {
      content.slideUp();
    } else {
      content.slideDown();
    }

    $(".collapsible").each(function () {
      var currentImg = $(this).find("img:first");
      var secondImg = $(this).find("img:nth-child(2)");

      if ($(this).hasClass("active")) {
        currentImg.addClass("disnone_icon");
        secondImg.removeClass("disnone_icon");
      } else {
        secondImg.addClass("disnone_icon");
        currentImg.removeClass("disnone_icon");
      }
    });
  });

  $(document).on("click", ".showoption", function () {
    $(".bodypage").removeClass("active_session");
    $(".showoption").removeClass("active_menu");
    var clickoption = $(this).data("option");
    $("#" + clickoption).addClass("active_session");
    $(this).addClass("active_menu");
  });

  $(document).on("keyup", "#searchInput", function () {
    var keyword = $(this).val();
    if (keyword.length > 3) {
      $.ajax({
        url: "/admin/search/member",
        type: "POST",
        data: { keyword: keyword },
        success: function (respone) {
          var html = "";

          $.each(respone, function (key, val) {
            html += `
              <li class="editmember" data-id="${val[0]}" style="margin-left:20px;list-style-type: none; display:flex;" class="flex">
                  <img style="width : 60px ; height : 70px ; border-radius: 5px;" src="/static/img/avata/${val[3]}" alt="">
                  <div style="display:block; margin-top:-15px">
                      <h3 class="flex-con">${val[1]}</h3>
                      <p class="flex-con">${val[4]}</p>
                  </div>
              </li>
                        `;
          });
          $("#searchOutput").html(html);
        },
        error: function (xhr) {
          console.log(xhr);
        },
      });
    }
  });
  // <button style="margin-right:7px;height:38px" class="btn btn-success editmember" data-id="${val[0]}">
  //     <i class="fa-solid fa-pen-to-square"></i>
  // </button>
  // <button style="margin-right:7px;" class="btn btn-success editmember" data-id="${val[0]}">
  //                                           <i class="fa-solid fa-pen-to-square"></i>
  //                                       </button>
  memberdata();
  function memberdata() {
    $.ajax({
      url: "/memberdata",
      type: "GET",
      success: function (response) {
        var html = "";
        $.each(response.response, function (key, val) {
          html += `
              <tr class="editmember" data-id="${val[0]}">
                  <td>${val[0]}</td>
                  <td>
                      <img style="width : 50px ; height : 50px" src="/static/img/avata/${val[3]}" alt="">
                  </td>
                  <td>${val[1]}</td>
                  <td>${val[4]}</td>       
              </tr>`;
        });
        $(".membertable").html(html); // Gán chuỗi HTML vào một phần tử có class "membertable"
      },
      error: function (xhr) {
        console.log(xhr);
      },
    });
  }
  $(document).on("click", ".editmember", function () {
    $("#informationUser").removeClass("hidden");
    var id = $(this).data("id");
    $("#Userinformation").attr("data-id", id);

    $.ajax({
      url: "/member/update/" + id,
      type: "GET",
      success: function (respone) {
        $("#avataInformation").html(
          `<img id="imagepreview" style="width : 200px" src="/static/img/avata/${respone.respone[3]}" alt="">`
        );
        $("#numberid").val(respone.respone[0]);
        $("#name").val(respone.respone[1]);
        $("#member").val(respone.respone[4]);
        $("#deletemember").attr("data-id", respone.respone[0]);
      },
      error: function (xhr) {
        console.log(xhr);
      },
    });
  });

  $(document).on("submit", "#Userinformation", function (e) {
    e.preventDefault();
    var id = $(this).attr("data-id");

    const formData = new FormData(this);

    $.ajax({
      url: "/member/update/finish/" + id,
      type: "POST",
      data: formData,
      processData: false,
      contentType: false,
      success: function (respone) {
        $("#informationUser").addClass("hidden");
        memberdata();
      },
      error: function (xhr) {
        console.log(xhr);
      },
    });
  });
  $(document).ready(function () {
    $("#avataupdate").on("change", function () {
      var input = this;
      if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function (e) {
          $("#imagepreview").attr("src", e.target.result);
        };
        reader.readAsDataURL(input.files[0]);
      }
    });
  });
  $(document).on("click", "#deletemember", function (e) {
    e.preventDefault();
    var id = $(this).data("id");
    $("#confirmdelete").removeClass("hidden");
    $(".close_confirm").removeClass("hidden");
    $(document).on("click", "#remove", function () {
      $.ajax({
        url: "/admin/deletemember/" + id,
        type: "POST",
        success: function (respone) {
          console.log(respone);
        },
        error: function (xhr) {
          console.log(xhr);
        },
      });
    });
  });
});
