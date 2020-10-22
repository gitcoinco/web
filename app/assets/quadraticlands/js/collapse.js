// COLLAPSE
//
// find all classes .collapse 
// 
// click div.question
// toggle visibility on div.awnser

const collapse = document.querySelectorAll(".collapse");

collapse.forEach(item => {
	item.addEventListener("click", () => {
		item.classList.toggle("visible");
	});
});