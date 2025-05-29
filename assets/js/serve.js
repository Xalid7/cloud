document.addEventListener("DOMContentLoaded", () => {
  // ELEMENTLAR
  const serveMealForm = document.getElementById("serveMealForm");
  const serveMealSelect = document.getElementById("serveMealSelect");
  const serveMessage = document.getElementById("serveMessage");
  const portionTableBody = document.getElementById("portionTableBody");

  const statusDiv = document.getElementById("attendanceStatus");
  const attendanceForm = document.getElementById("attendanceForm");
  const attendanceInput = document.getElementById("attendanceCountInput");

  // 🍽 1. Ovqat ro'yxatini yuklash
  function loadMealOptions() {
    fetch("/api/meals/")
      .then(res => res.json())
      .then(data => {
        serveMealSelect.innerHTML = "";
        data.forEach(meal => {
          const option = document.createElement("option");
          option.value = meal.id;
          option.textContent = meal.name;
          serveMealSelect.appendChild(option);
        });
      });
  }

  // 📥 2. Davomatni olish (return count)
  async function loadAttendanceCount() {
    try {
      const res = await fetch("/attendance/today");
      if (!res.ok) throw new Error("Xatolik");
      const data = await res.json();
      return data?.count || null;
    } catch (err) {
      console.error("Davomatni olishda xatolik:", err);
      return null;
    }
  }

  // 📊 3. Davomatni UI’da ko‘rsatish
  async function renderAttendanceStatus() {
    try {
      const res = await fetch("/attendance/today");
      const data = await res.json();

      if (data === null) {
        statusDiv.innerHTML = "⚠️ Bugungi davomat hali kiritilmagan.";
        statusDiv.className = "alert alert-warning mt-3";
      } else {
        statusDiv.innerHTML = `👶 <strong>Bugun ${data.count} nafar bola qatnashmoqda.</strong>`;
        statusDiv.className = "alert alert-success mt-3";
      }
    } catch (err) {
      statusDiv.innerHTML = "❌ Davomatni yuklashda xatolik yuz berdi.";
      statusDiv.className = "alert alert-danger mt-3";
    }
  }

  // 📌 4. Har bir ovqat uchun porsiyani olish
  async function getMealPortion(mealId) {
    try {
      const res = await fetch(`/api/meal-portions/${mealId}`);
      if (!res.ok) throw new Error("Porsiyani olishda xatolik");
      const data = await res.json();
      return data.portions;
    } catch (err) {
      console.error("Porsiya olishda xatolik:", err);
      return 0;
    }
  }

  // ✅ 5. Ovqat berish tugmasi ishlaganda
  serveMealForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const mealId = serveMealSelect.value;

    const attendanceCount = await loadAttendanceCount();
    if (attendanceCount === null) {
      alert("⚠️ Bugungi davomat kiritilmagan. Ovqat berish mumkin emas.");
      return;
    }

    const availablePortions = await getMealPortion(mealId);
    if (availablePortions < attendanceCount) {
      alert(`❌ Ingredient yetarli emas! Porsiya mavjud: ${availablePortions}, kerakli: ${attendanceCount}`);
      return;
    }

    // Serve qilish
    fetch("/api/serve-meal/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ meal_id: mealId })
    })
    .then(res => res.json().then(data => ({ status: res.status, data })))
    .then(({ status, data }) => {
      serveMessage.classList.remove("d-none", "alert-danger", "alert-success");
      if (status === 200) {
        serveMessage.classList.add("alert-success");
        serveMessage.textContent = "✅ Ovqat muvaffaqiyatli berildi!";
        updatePortionTable();
      } else {
        serveMessage.classList.add("alert-danger");
        serveMessage.textContent = "❌ Xatolik: " + (data.detail || "Ingredient yetarli emas");
      }
    })
    .catch(err => {
      serveMessage.classList.remove("d-none");
      serveMessage.classList.add("alert-danger");
      serveMessage.textContent = "❌ Tarmoq xatosi: " + err.message;
    });
  });

  // 🔁 6. Porsiyalar jadvalini yangilash
  function updatePortionTable() {
    fetch("/api/meal-portions/")
      .then(res => res.json())
      .then(data => {
        portionTableBody.innerHTML = "";
        data.forEach(item => {
          const row = `
            <tr>
              <td>${item.meal_name}</td>
              <td>${item.portions}</td>
            </tr>`;
          portionTableBody.innerHTML += row;
        });
      });
  }

  // ➕ 7. Davomatni saqlash (POST)
  attendanceForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const count = parseInt(attendanceInput.value);

    try {
      const res = await fetch("/attendance/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ count: count, date: new Date().toISOString().split("T")[0] })
      });

      if (!res.ok) throw new Error("Davomatni saqlab bo‘lmadi");

      await renderAttendanceStatus();
      attendanceInput.value = "";
    } catch (err) {
      alert("❌ Davomatni yuborishda xatolik: " + err.message);
    }
  });

  // 🔃 Boshlanishida yuklashlar
  loadMealOptions();
  updatePortionTable();
  renderAttendanceStatus();
});

