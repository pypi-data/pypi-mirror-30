/**
 * Created by pedroreis on 12/03/18.
 */
$(function() {
    $('[data-lang]').hide();
    var lang = $('#id_lang');

    if(lang.val() !== '') {
        $('[data-lang="__lang__"]'.replace('__lang__',lang.val())).show();
    }

    lang.on('change',function(){
        $('[data-lang]').hide();
        $('[data-lang="__lang__"]'.replace('__lang__',$(this).val())).show();
    });
});