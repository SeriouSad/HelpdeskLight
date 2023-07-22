document.querySelector('.burger-icon').addEventListener('click', function() {
  this.classList.toggle('active');
  document.querySelector('.sidebar').classList.toggle('active');
});