// COLLAPSE
//
// find all classes .collapse 
// 
// on click toggle class "visible"

const collapse = document.querySelectorAll(".collapse");

collapse.forEach(item => {
	item.addEventListener("click", () => {
		item.classList.toggle("visible");
	});
});