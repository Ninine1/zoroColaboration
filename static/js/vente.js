document.addEventListener("DOMContentLoaded", function () {
  var produitSelect = document.querySelector(".produit-select");
  var quantiteInput = document.querySelector(".quantite-input");
  var prixTotalSpan = document.querySelector(".prix-total-span");

  // Fonction pour mettre à jour le prix total
  function updatePrixTotal() {
    var id_produit = produitSelect.value;

    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/get_prix_unitaire/" + id_produit, true);
    xhr.onreadystatechange = function () {
      if (xhr.readyState === 4 && xhr.status === 200) {
        var response = JSON.parse(xhr.responseText);
        var prix_unitaire = response.prix_unitaire;

        if (prix_unitaire !== null) {
          var quantite = parseInt(quantiteInput.value, 10);
          var prix_total = quantite * prix_unitaire;
          prixTotalSpan.textContent = "Prix Total: $" + prix_total.toFixed(2);
        } else {
          // Gérer le cas où le prix unitaire n'est pas disponible
          prixTotalSpan.textContent = "Prix Total: N/A";
        }
      }
    };
    xhr.send();
  }

  // Événements pour déclencher la mise à jour du prix total lors des changements de quantité et de produit
  quantiteInput.addEventListener("input", updatePrixTotal);
  produitSelect.addEventListener("change", updatePrixTotal);

  // Appeler la fonction initiale au chargement de la page
  updatePrixTotal();
});
