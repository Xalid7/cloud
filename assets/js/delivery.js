async function drawDeliveryChart() {
  const res = await fetch("/reports/delivered/");
  const data = await res.json();

  const series = [{
    name: "Yetkazilgan",
    data: data.map(row => ({
      x: row.date,
      y: row.quantity
    }))
  }];

  const chart = new ApexCharts(document.querySelector("#ingredientDeliveryChart"), {
    chart: {
      type: "bar",
      height: 300
    },
    series,
    xaxis: {
      type: "datetime"
    }
  });

  chart.render();
}

drawDeliveryChart();
