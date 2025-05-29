document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("mealForm");
  const nameInput = document.getElementById("mealName");
  const dateInput = document.getElementById("mealDate");
  const table = document.getElementById("mealTableBody");
  const ingredientSelect = document.getElementById("mealIngredients");

  let meals = [];

  // 🔄 Ingredientlar select'ga yuklanadi
  async function loadIngredients() {
    try {
      const res = await fetch("/api/ingredients/");
      if (!res.ok) throw new Error("Ingredientlarni olib bo‘lmadi");
      const items = await res.json();

      ingredientSelect.innerHTML = "";
      items.forEach(ing => {
        const option = document.createElement("option");
        option.value = ing.id;
        option.textContent = ing.name;
        ingredientSelect.appendChild(option);
      });
    } catch (err) {
      console.error("Ingredient yuklashda xatolik:", err);
    }
  }

  // 📥 Ovqatlar ro'yxati
  async function loadMeals() {
    try {
      const res = await fetch("/api/meals/");
      if (!res.ok) throw new Error("Ovqatlarni olishda xatolik");
      meals = await res.json();
      renderMeals();
    } catch (err) {
      console.error("Ovqatlarni yuklashda xatolik:", err);
    }
  }

  // 📋 Jadvalni chiqarish
  function renderMeals() {
    table.innerHTML = "";
    meals.forEach((meal, i) => {
      const ingredientsHTML = meal.ingredients && meal.ingredients.length > 0
        ? meal.ingredients.map(ing => `${ing.ingredient.name} (${ing.amount_grams}g)`).join(", ")
        : "<em>Ingredientlar yo‘q</em>";

      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${i + 1}</td>
        <td>
          <strong>${meal.name}</strong><br/>
          <small>${ingredientsHTML}</small>
        </td>
        <td>${meal.cooked_at ? new Date(meal.cooked_at).toLocaleString() : '-'}</td>
        <td>
          <button class="btn btn-danger btn-sm btn-delete" data-id="${meal.id}">🗑 O‘chirish</button>
        </td>`;
      table.appendChild(row);
    });

    document.querySelectorAll(".btn-delete").forEach(btn => {
      btn.addEventListener("click", async (e) => {
        const id = e.target.dataset.id;
        await deleteMeal(id);
      });
    });
  }

  // ❌ Ovqatni o‘chirish
  async function deleteMeal(id) {
    try {
      const res = await fetch(`/api/meals/${id}`, { method: "DELETE" });
      if (!res.ok) throw new Error("O‘chirishda xatolik");
      meals = meals.filter(m => m.id !== parseInt(id));
      renderMeals();
    } catch (err) {
      console.error("O‘chirishda xatolik:", err);
    }
  }

  // ➕ Qo‘shish
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const name = nameInput.value.trim();
    const cooked_at_raw = dateInput.value;
    const selectedOptions = [...ingredientSelect.selectedOptions];

    if (!name || !cooked_at_raw || selectedOptions.length === 0) {
      alert("Barcha maydonlar to‘ldirilishi kerak!");
      return;
    }

    const cooked_at = new Date(cooked_at_raw).toISOString();

    const ingredients = selectedOptions.map(opt => ({
      ingredient_id: parseInt(opt.value),
      amount_grams: 100  // bu yerda istasangiz foydalanuvchi kiritadigan qiling
    }));

    const payload = { name, cooked_at, ingredients };

    try {
      const res = await fetch("/api/meals/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const newMeal = await res.json();

      if (!res.ok) {
        const msg = typeof newMeal.detail === "string"
          ? newMeal.detail
          : JSON.stringify(newMeal.detail);
        alert("❌ Xatolik: " + msg);
        return;
      }

      meals.push(newMeal);
      renderMeals();
      form.reset();

      const modal = bootstrap.Modal.getInstance(document.getElementById("mealModal"));
      modal?.hide();
    } catch (err) {
      console.error("Qo‘shishda xatolik:", err);
      alert("❌ Qo‘shishda xatolik: " + err.message);
    }
  });

  // 🚀 Boshlang‘ich yuklash
  loadIngredients();
  loadMeals();
});
