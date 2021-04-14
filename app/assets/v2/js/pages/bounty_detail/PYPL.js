
const payWithPYPL = (fulfillment_id, fulfiller_identifier, ele, vm, modal) => {
  const amount = vm.fulfillment_context.amount;

  paypal.Buttons(
    {
      style: {
        color: 'blue'
      },
      createOrder: function(data, actions) {
        return actions.order.create({
          application_context: {
            shipping_preference: 'NO_SHIPPING'
          },
          purchase_units: [{
            payee: {
              email_address: fulfiller_identifier
            },
            amount: {
              value: amount
            }
          }]
        });
      },
      onApprove: function(data, actions) {
        return actions.order.capture().then(function(details) {
          console.log('Bounty Paid via', details.payer.name);

          const payload = {
            payout_type: 'fiat',
            tenant: 'PYPL',
            amount: amount,
            token_name: 'USD',
            funder_identifier: details.payer && details.payer.email_address,
            payout_tx_id: details.id,
            payout_status: details.status == 'COMPLETED' ? 'done' : 'expired'
          };

          const apiUrlBounty = `/api/v1/bounty/payout/${fulfillment_id}`;

          fetchData(apiUrlBounty, 'POST', payload).then(response => {
            if (200 <= response.status && response.status <= 204) {
              console.log('success', response);

              vm.fetchBounty();
              modal.closeModal();
              $(ele).html('');
              _alert('Payment Successful');

            } else {
              _alert('Unable to make payout bounty. Please try again later', 'danger');
              console.error(`error: bounty payment failed with status: ${response.status} and message: ${response.message}`);
            }
          }).catch(function(error) {
            _alert('Unable to make payout bounty. Please try again later', 'danger');
            console.log(error);
          });

        }).catch(function(error) {
          _alert('Unable to make payout bounty. Please try again later', 'danger');
          console.log(error);
        });
      }
    }
  ).render(ele);
};
