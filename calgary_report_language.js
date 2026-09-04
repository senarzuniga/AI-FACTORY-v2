function setLanguage(language) {
  document.documentElement.lang = language;
  document.querySelectorAll('.lang').forEach((element) => {
    element.classList.toggle('hidden', !element.classList.contains(`lang-${language}`));
  });
  document.querySelectorAll('[data-language]').forEach((button) => {
    button.setAttribute('aria-pressed', String(button.dataset.language === language));
  });
}

document.querySelectorAll('[data-language]').forEach((button) => {
  button.addEventListener('click', () => setLanguage(button.dataset.language));
});