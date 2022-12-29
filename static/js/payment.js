$(document).ready(function () {

    //COUPON
    $(document).on('click', '#apply_coupon',function () {

        var coupon_code = $("[name='coupon_code']").val();
        var order_number = $('.order_number').attr('order_number');
        // var errorDisplay = $('#error').innerHTML;
        console.log(order_number, coupon_code);
        // console.log(errorDisplay);

        //ajax
        $.ajax({
            url: "/orders/apply-coupon/",
            data: {
                'coupon_code':coupon_code,
                'order_number':order_number
            },
            dataType: "json",
            success: function (res) {
                // console.log(res);
                if (res.msg=='Coupon is Applied') {
                    swal(res.msg);
                    // document.getElementById(res.msg).innerHTML
                    // swal.fire("Congratulations ! ", res.msg, "success")
                    $('#payment_render').html(res.data);
                } else{
                    swal(res.msg);
                    // alert(res.msg)
                    // document.getElementById(res.msg).innerHTML


                }
            }
        });
        //End Ajax
        
    });
    //End coupon



    



    //Remove Cart
    // $(document).on('click', '#remove_cart_item',function () {

        // var coupon_code = $("[name='coupon_code']").val();
        // var order_number = $('.order_number').attr('order_number');
        // var errorDisplay = $('#error').innerHTML;
        // console.log(order_number, coupon_code);
        // console.log(errorDisplay);

        //ajax
        // $.ajax({
        //     url: "/cart/remove_cart_item/",
        //     // data: {
            //     'coupon_code':coupon_code,
            //     'order_number':order_number
            // },
            // dataType: "json",
                // swal({
                //     title: "Are you sure?",
                //     text: "Once deleted, you will not be able to recover this imaginary file!",
                //     icon: "warning",
                //     buttons: true,
                //     dangerMode: true,
                // })
                // .then((willDelete) => {
                //     if (willDelete) {
                //     swal("Poof! Your imaginary file has been deleted!", {
                //         icon: "success",
                //     });
                //     } else {
                //     swal("Your imaginary file is safe!");
                //     }
                
            // success: function (res) {
                // console.log(res);
                // if (res.msg=='Item Removed') {
                //     swal(res.msg);
                    // document.getElementById(res.msg).innerHTML
                    // swal.fire("Congratulations ! ", res.msg, "success")
                    // $('#payment_render').html(res.data);
                // } else{
                //     swal(res.msg);
                    // alert(res.msg)
                    // document.getElementById(res.msg).innerHTML


                // }
            // }
        // });
        //End Ajax
        
    // });


});