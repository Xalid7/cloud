document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('ingredientForm');
  const table = document.getElementById('ingredientTableBody');
  const nameInput = document.getElementById('ingredientName');
  const qtyInput = document.getElementById('ingredientQty');
  const dateInput = document.getElementById('ingredientDate');

  const editForm = document.getElementById('editIngredientForm');
  const editIdInput = document.getElementById('editIngredientId');
  const editNameInput = document.getElementById('editIngredientName');
  const editQtyInput = document.getElementById('editIngredientQty');
  const editDateInput = document.getElementById('editIngredientDate');

  let data = [];

  // 🔄 Ingredientlar ro‘yxatini yuklash
  async function loadIngredients() {
    try {
      const response = await fetch("/api/ingredients/");
      if (!response.ok) throw new Error("Serverdan ma'lumot olib bo‘lmadi");
      data = await response.json();
      renderIngredients();
    } catch (error) {
      console.error("❌ Ma'lumot yuklashda xatolik:", error);
    }
  }

  // 📋 Ingredientlarni jadvalga chiqarish
  function renderIngredients() {
    table.innerHTML = '';
    data.forEach((item, index) => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${index + 1}</td>
        <td>${item.name}</td>
        <td>${item.quantity_grams ?? '-'} g</td>
        <td>${formatDate(item.delivered_at)}</td>
        <td>
          <button data-id="${item.id}" class="btn btn-sm btn-primary btn-edit">✏️</button>
          <button data-id="${item.id}" class="btn btn-sm btn-danger btn-delete">🗑</button>
        </td>`;
      table.appendChild(row);
    });

    // Hodisalar biriktirish
    document.querySelectorAll(".btn-delete").forEach(button => {
      button.addEventListener("click", async (e) => {
        const id = e.target.dataset.id;
        await deleteIngredient(id);
      });
    });

    document.querySelectorAll(".btn-edit").forEach(button => {
      button.addEventListener("click", () => {
        const id = button.dataset.id;
        const item = data.find(i => i.id === parseInt(id));
        if (item) {
          editIdInput.value = item.id;
          editNameInput.value = item.name;
          editQtyInput.value = item.quantity_grams;
          editDateInput.value = item.delivered_at;

          const modal = new bootstrap.Modal(document.getElementById('editIngredientModal'));
          modal.show();
        }
      });
    });
  }

  // 📅 Sanani formatlash
  function formatDate(dateString) {
    if (!dateString) return "-";
    const date = new Date(dateString);
    return `${String(date.getDate()).padStart(2, '0')}.${String(date.getMonth() + 1).padStart(2, '0')}.${date.getFullYear()}`;
  }

  // ❌ Ingredientni o‘chirish
  async function deleteIngredient(id) {
    try {
      const res = await fetch(`/api/ingredients/${id}`, { method: 'DELETE' });
      if (!res.ok) throw new Error("Serverda o‘chirishda xatolik");
      data = data.filter(item => item.id !== parseInt(id));
      renderIngredients();
    } catch (error) {
      console.error("❌ O‘chirishda xatolik:", error);
      alert("O‘chirishda xatolik yuz berdi.");
    }
  }

  // ➕ Yangi ingredient qo‘shish
  form?.addEventListener('submit', async (e) => {
    e.preventDefault();

    const newItem = {
      name: nameInput.value.trim(),
      quantity_grams: parseFloat(qtyInput.value),
      delivered_at: dateInput.value
    };

    if (!newItem.name || isNaN(newItem.quantity_grams) || !newItem.delivered_at) {
      alert("❗ Iltimos, barcha maydonlarni to‘ldiring.");
      return;
    }

    try {
      const response = await fetch("/api/ingredients/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newItem)
      });

      const addedItem = await response.json();

      if (!response.ok) {
        const message = addedItem?.detail || "Qo‘shib bo‘lmadi.";
        alert("❌ Xatolik: " + message);
        return;
      }

      data.push(addedItem);
      form.reset();

      const modalEl = document.getElementById('ingredientModal');
      const modal = bootstrap.Modal.getInstance(modalEl);
      modal?.hide();

      renderIngredients();
    } catch (error) {
      console.error("❌ Qo‘shishda xatolik:", error);
      alert("Qo‘shishda xatolik yuz berdi.");
    }
  });

  // 📝 Ingredientni yangilash
  editForm?.addEventListener("submit", async (e) => {
    e.preventDefault();

    const id = editIdInput.value;
    const updatedItem = {
      name: editNameInput.value.trim(),
      quantity_grams: parseFloat(editQtyInput.value),
      delivered_at: editDateInput.value
    };

    if (!updatedItem.name || isNaN(updatedItem.quantity_grams) || !updatedItem.delivered_at) {
      alert("❗ Iltimos, barcha maydonlarni to‘ldiring.");
      return;
    }

    try {
      const response = await fetch(`/api/ingredients/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updatedItem)
      });

      if (!response.ok) {
        const error = await response.json();
        alert("❌ Xatolik: " + (error?.detail || "Yangilab bo‘lmadi."));
        return;
      }

      // Mahalliy datani yangilash
      const index = data.findIndex(i => i.id === parseInt(id));
      if (index !== -1) data[index] = { ...data[index], ...updatedItem };

      const modal = bootstrap.Modal.getInstance(document.getElementById('editIngredientModal'));
      modal?.hide();

      renderIngredients();
    } catch (error) {
      console.error("❌ Yangilashda xatolik:", error);
      alert("Yangilashda xatolik yuz berdi.");
    }
  });

  // 🚀 Boshlanishida ingredientlar yuklash
  loadIngredients();
});
