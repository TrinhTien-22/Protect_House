$(".button_warning").click(function () {
  var dataform = $(this).attr("data-warning");
  if (dataform == "") {
    $(".text_notselect").removeClass("disnone");
    $(".form_temperature").addClass("disnone");
    $(".form_humidity").addClass("disnone");
    $(".form_light").addClass("disnone");
  }
  if (dataform == "temperature") {
    $(".form_temperature").removeClass("disnone");
    $(".form_humidity").addClass("disnone");
    $(".form_light").addClass("disnone");
    $(".text_notselect").addClass("disnone");
  }
  if (dataform == "humidity") {
    $(".form_temperature").addClass("disnone");
    $(".form_humidity").removeClass("disnone");
    $(".form_light").addClass("disnone");
    $(".text_notselect").addClass("disnone");
  }
  if (dataform == "light") {
    $(".form_temperature").addClass("disnone");
    $(".form_humidity").addClass("disnone");
    $(".form_light").removeClass("disnone");
    $(".text_notselect").addClass("disnone");
  }
  $(".content_close").removeClass("disnone");
});
$(document).on("click", ".close_infor", function () {
  $(".content_close").addClass("disnone");
});
var socket = io.connect("http://" + "127.0.0.1" + ":" + "5000");

var chart = Highcharts.chart("container", {
  chart: {
    zoomType: "xy",
  },
  title: {
    text: "Đồ thị nhiệt độ - độ ẩm - ánh sáng",
  },

  xAxis: [
    {
      categories: [],
      tickWidth: 1,
      tickLength: 20,
    },
  ],
  yAxis: [
    {
      // Primary yAxis
      labels: {
        format: "{value}",
        style: {
          color: Highcharts.getOptions().colors[1],
        },
      },
      title: {
        text: "Number of Employees",
        style: {
          color: Highcharts.getOptions().colors[1],
        },
      },
    },
  ],

  series: [
    {
      name: "Độ ẩm",
      // type: 'column',
      type: "spline",
      data: [],
      tooltip: {
        valueSuffix: "%",
      },
      // color: "yellow"
    },
    {
      name: "Nhiệt độ",
      type: "spline",
      data: [],
      tooltip: {
        valueSuffix: "°C",
      },
    },
    {
      name: "Ánh sáng",
      type: "spline",
      data: [],
      tooltip: {
        valueSuffix: "lux",
      },
    },
  ],
});
var temp = [];
var humi = [];
var light = [];
socket.on("send-data-temp", function (data) {
  temp.push(data);
  if (temp.length > 1) {
    temp.shift();
  }
  chart.series[1].setData(data);
});

socket.on("send-data-humi", function (data) {
  humi.push(data);
  if (humi.length > 1) {
    humi.shift();
  }
  chart.series[0].setData(data);
});

socket.on("send-data-light", function (data) {
  light.push(data);
  if (light.length > 1) {
    light.shift();
  }
  chart.series[2].setData(data);
});
function displayValues(matrix, text) {
  if (text === "temp") {
    $(".text_dht11").html("Temperature");
    $(".button_warning").attr("data-warning", "temperature");
  }
  if (text === "humi") {
    $(".text_dht11").html("Humidity");
    $(".button_warning").attr("data-warning", "humidity");
  }
  if (text === "light") {
    $(".text_dht11").html("Light");
    $(".button_warning").attr("data-warning", "light");
  }
  if (matrix[0].length <= 5) {
    if (matrix[0][1] <= matrix[0][4]) {
      $(".arrow_down").addClass("hidden");
      $(".arrow_up").removeClass("hidden");
    } else {
      $(".arrow_up").addClass("hidden");
      $(".arrow_down").removeClass("hidden");
    }
    $(".display_array").html(
      "<p>" +
        JSON.stringify(matrix[0][0]) +
        "</p>" +
        "<p>" +
        JSON.stringify(matrix[0][1]) +
        "</p>" +
        "<p>" +
        JSON.stringify(matrix[0][2]) +
        "</p>" +
        "<p>" +
        JSON.stringify(matrix[0][3]) +
        "</p>" +
        "<p>" +
        JSON.stringify(matrix[0][4]) +
        "</p>"
    );
  } else if (5 > matrix[0].length <= 10) {
    if (matrix[0][5] <= matrix[0][9]) {
      $(".arrow_down").addClass("hidden");
      $(".arrow_up").removeClass("hidden");
    } else {
      $(".arrow_up").addClass("hidden");
      $(".arrow_down").removeClass("hidden");
    }
    $(".display_array").html(
      "<p>" +
        JSON.stringify(matrix[0][5]) +
        "</p>" +
        "<p>" +
        JSON.stringify(matrix[0][6]) +
        "</p>" +
        "<p>" +
        JSON.stringify(matrix[0][7]) +
        "</p>" +
        "<p>" +
        JSON.stringify(matrix[0][8]) +
        "</p>" +
        "<p>" +
        JSON.stringify(matrix[0][9]) +
        "</p>"
    );
  } else if (matrix[0].length > 10) {
    if (matrix[0][10] <= matrix[0][14]) {
      $(".arrow_down").addClass("hidden");
      $(".arrow_up").removeClass("hidden");
    } else {
      $(".arrow_up").addClass("hidden");
      $(".arrow_down").removeClass("hidden");
    }
    $(".display_array").html(
      "<p>" +
        JSON.stringify(matrix[0][9]) +
        "</p>" +
        "<p>" +
        JSON.stringify(matrix[0][10]) +
        "</p>" +
        "<p>" +
        JSON.stringify(matrix[0][11]) +
        "</p>" +
        "<p>" +
        JSON.stringify(matrix[0][12]) +
        "</p>" +
        "<p>" +
        JSON.stringify(matrix[0][13]) +
        "</p>"
    );
  }
}
// Lấy giá trị từ các phần tử HTML
// var currentTemp = parseFloat($('#currentTemp').text()); // Chuyển giá trị thành số thập phân
// var currentHumi = parseFloat($('#currentHumi').text()); // Chuyển giá trị thành số thập phân
// var currentLight = parseFloat($('#currentLight').text()); // Chuyển giá trị thành số thập phân

// // Cập nhật dữ liệu của biểu đồ
// chart.series[0].addPoint([xAxis, currentHumi]); // xValue là thời gian hoặc vị trí dữ liệu của độ ẩm
// chart.series[1].addPoint([xAxis, currentTemp]); // xValue là thời gian hoặc vị trí dữ liệu của nhiệt độ
// chart.series[2].addPoint([xAxis, currentLight]);

$(".warningsubmit").on("click", function (e) {
  e.preventDefault(); // Ngăn chặn gửi form mặc định
  $(".content_close").addClass("disnone");
  var dataType = $(this).data("type"); // Lấy loại dữ liệu từ data-type

  var value = $("#" + dataType).val(); // Lấy giá trị từ trường input

  $.ajax({
    url: "/home/livingroom/warning",
    type: "POST",
    data: { dataType: dataType, [dataType]: value }, // Tạo đối tượng dữ liệu với key dựa vào dataType
    success: function (response) {
      console.log(response);
      warning();
    },
    error: function (xhr) {
      console.log(xhr);
    },
  });
});

function warning() {
  $.ajax({
    url: "/home/livingroom/getinforwarning",
    type: "GET",
    success: function (response) {
      $("#warning_temperature").text(response[1]);
      $("#warning_humidity").text(response[2]);
      $("#warning_light").text(response[3]);
    },
    error: function (xhr) {
      console.log(xhr);
    },
  });
}
function updateData() {
  $.ajax({
    url: "/home/livingroom/data", // Route mới để lấy dữ liệu từ máy chủ Flask
    type: "GET",
    success: function (response) {
      // console.log(response);
      // Cập nhật dữ liệu trên trang web với dữ liệu mới
      $("#currentTemp").text(response.Response.Temperature);
      $("#currentHumi").text(response.Response.Humidity);
      $("#currentLight").text(response.Response.Light);
    },
  });
}

$(document).ready(function () {
  warning();
  updateData();
  // setInterval(updateData, 10000);
});
