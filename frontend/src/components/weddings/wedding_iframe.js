import React from 'react';

function WeddingsIframeComponent() {
  return (
    <div>
        <h1>Request Form</h1>
        <iframe
          style={{ width: "100%", height: "500px", border: "none", borderRadius: "0px" }}
            src="https://api.leadconnectorhq.com/widget/form/vRJLRAlCd3N4acsqDbdn"
            id="inline-vRJLRAlCd3N4acsqDbdn" 
            data-layout="{'id':'INLINE'}"
            data-trigger-type="alwaysShow"
            data-trigger-value=""
            data-activation-type="alwaysActivated"
            data-activation-value=""
            data-deactivation-type="neverDeactivate"
            data-deactivation-value=""
            data-form-name="Pricing Pamphlet Capture Form"
            data-height="582"
            data-layout-iframe-id="inline-vRJLRAlCd3N4acsqDbdn"
            data-form-id="vRJLRAlCd3N4acsqDbdn"
            title="Pricing Pamphlet Capture Form"
            >
        </iframe>
        <script src="https://link.msgsndr.com/js/form_embed.js"></script>
    </div>
  );
}

export default WeddingsIframeComponent;