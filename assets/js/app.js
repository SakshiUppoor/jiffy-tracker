var DOMStrings = {
    addBtn: '.addBtn',
    form: '.form'
};
var onClickAdd = function() {
    var html ='<SELECT class = "options" name="element">{% for sub in subs %}{% if sub.semester.id == sem.id %}<OPTION value="{{sub.id}}">Saurav</OPTION><br>{% endif %} {% endfor %} </SELECT>';
    document.querySelector(DOMStrings.form).insertAdjacentHTML('beforeend', html);
    console.log('Button clicked');
}
console.log('JS working');
document.querySelector(DOMStrings.addBtn).addEventListener('click', onClickAdd);
