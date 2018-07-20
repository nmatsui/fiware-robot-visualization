'use strict';

export default () => {
    const $st_datetime = $("#st_datetime");
    const $et_datetime = $("#et_datetime");
    const $show_button = $("button#show_button");
    $show_button.prop("disabled", true);

    const datePickerOptions = {
        locale: 'ja',
        icons: {
            time: 'fa fa-clock',
        }
    };

    const changeHandler = (date, oldDate) => {
        const st = $("input#st_datetime_value").val();
        const et = $("input#et_datetime_value").val();
        if (st && et) {
            $show_button.prop("disabled", false);
        } else {
            $show_button.prop("disabled", true);
        }
    };

    $st_datetime.datetimepicker(datePickerOptions);
    $et_datetime.datetimepicker(datePickerOptions);

    $st_datetime.on('change.datetimepicker', changeHandler);
    $et_datetime.on('change.datetimepicker', changeHandler);
}
