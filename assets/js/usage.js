document.addEventListener("DOMContentLoaded", () => {
  fetch("/api/dashboard/usage-report")
    .then(res => res.json())
    .then(data => {
      const labels = data.map(item => item.name);
      const values = data.map(item => item.total_used);

      const options = {
        chart: { type: 'bar', height: 350 },
        series: [{ name: "Iste'mol", data: values }],
        xaxis: { categories: labels }
      };

      const chart = new ApexCharts(document.querySelector("#usage-chart"), options);
      chart.render();
    })
    .catch(err => console.error("Grafikda xatolik:", err));
});
