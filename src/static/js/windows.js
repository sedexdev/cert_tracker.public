/**
 * Displays the window for deleting a
 * resource
 *
 * @param {string} id - element ID
 */
function displayWindow(id) {
  const el = document.getElementById(id);
  if (el) {
    el.classList.remove("hidden");
  }
}

/**
 * Hides the resource window
 *
 * @param {string} id - element ID
 */
function hideWindow(id) {
  const el = document.getElementById(id);
  if (el) {
    el.classList.add("hidden");
  }
}

/**
 * Displays the window for deleting a cert
 *
 * @param {Event} e
 * @param {number} id
 */
function displayCertWindow(e, id) {
  e.preventDefault();
  if (e && e.stopPropagation) {
    e.stopPropagation();
    displayWindow(id);
  }
}
