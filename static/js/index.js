$(document).ready(function () {
  $(document).on("click", ".admin_show_hide", function () {
    $(".nt_show_pass").toggleClass("active");
    $(".nt_hide_pass").toggleClass("active");
    $("#passwordadmin").attr(
      "type",
      $("#passwordadmin").attr("type") == "password" ? "text" : "password"
    );
  });
  let slideIndex = 0;

  showSlides();

  $(".prev").on("click", function () {
    plusSlides(-1);
  });

  $(".next").on("click", function () {
    plusSlides(1);
  });

  function plusSlides(n) {
    showSlides((slideIndex += n));
  }

  function showSlides() {
    let slides = $(".slide");

    if (slideIndex >= slides.length) {
      slideIndex = 0;
    }

    if (slideIndex < 0) {
      slideIndex = slides.length - 1;
    }

    slides.hide();
    slides.eq(slideIndex).show();

    slideIndex++;

    setTimeout(showSlides, 5000); // Chuyển ảnh sau 5 giây
  }
  memberdata();
  function memberdata() {
    $.ajax({
      url: "/memberdata",
      type: "GET",
      success: function (response) {
        var html = "";
        $.each(response.response, function (key, val) {
          html += `
                    <div class=" informember col-sm-6 col-md-4 col-lg-3 p-b-35 isotope-item women"
                        style="  margin-left:10px; max-width:290px ; border-radius: 10px;">
                    <div class="block2" >
                    <div class="block2-pic hov-img0" style="border-radius: 10px;">
                        <img style="height:165px ;" src="/static/img/avata/${val[3]}" alt="IMG-PRODUCT">

                        <form data-id="${val[0]}"
                            class="block2-btn flex-c-m stext-103 cl2 size-102 bg0 bor2 hov-btn1 p-lr-15 trans-04 js-show-modal1">
                            Quick View
                        </form>
                    </div>

                    <div class="block2-txt flex-w flex-t p-t-14">
                        <div class="block2-txt-child1 flex-col-l ">
                            <a href="#" class="stext-104 cl4 hov-cl1 trans-04 js-name-b2 p-b-6">
                                ${val[1]}
                            </a>

                            <span class="stext-105 cl3">
                                ${val[4]}
                            </span>
                        </div>

                        <div class="block2-txt-child2 flex-r p-t-3">
                            <a href="#" class="btn-addwish-b2 dis-block pos-relative js-addwish-b2">
                                <img class="icon-heart1 dis-block trans-04" src="/static/img/icon/icon-heart-01.png"
                                    alt="ICON">
                                <img class="icon-heart2 dis-block trans-04 ab-t-l"
                                    src="/static/img/icon/icon-heart-02.png" alt="ICON">
                            </a>
                        </div>
                    </div>
                </div>
            </div>
            `;
        });
        $(".memberover").html(html);
      },
      error: function (xhr) {
        console.log(xhr);
      },
    });
  }

  // $(document).on("click", '.editmember', function () {

  //     $("#informationUser").removeClass("hidden");
  //     var id = $(this).data('id');
  //     $('#Formlogin').attr('data-id', id);
  //     $.ajax({
  //         url: "/member/update/" + id,
  //         type: 'GET',
  //         success: function (respone) {

  //             $('#avataInformation').html(`<img style="width : 200px" src="/static/img/avata/${respone.respone[2]}" alt="">`);
  //             $('#numberid').val(respone.respone[0]);
  //             $('#name').val(respone.respone[1]);
  //             $('#member').val(respone.respone[3]);
  //         },
  //         error: function (xhr) {
  //             console.log(xhr);
  //         }
  //     })
  // });
  // $(document).on('submit', '#Formlogin', function (e) {
  //     e.preventDefault();
  //     var id = $(this).data('id');
  //     var data = $(this).serialize();
  //     console.log(data);
  //     $.ajax({
  //         url: "/member/update/finish/" + id,
  //         type: "POST",
  //         data: data,
  //         success: function (respone) {
  //             $("#loginForm").addClass("hidden");
  //             memberdata();
  //         },
  //         error: function (xhr) {
  //             console.log(xhr);
  //         }
  //     });
  // });
  $(document).on("submit", "#Adminlogin", function (e) {
    e.preventDefault();
    $.ajax({
      url: "/admin/login",
      data: $(this).serialize(),
      type: "POST",
      success: function (respone) {
        console.log(respone);
        if (respone == "ok") {
          window.location.href = "/admin";
        } else {
          $(".showerror").html(
            '<p style="color: red;">Tài khoản hoặc mật khẩu sai !</p>'
          );
        }
      },
      error: function (xhr) {
        console.log(xhr);
      },
    });
  });
});
