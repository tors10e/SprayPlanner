'use strict';

function CabernetModal(props) {
    return (
    <Modal
        id="cabernet-modal"
        jquery_id="#cabernet-modal"
        image_source="./images/1000x1000/cab_sav_1000x1000.jpg"
        name="Cabernet Sauvignon"
        modal_text="Notes of plum, black cherry and tobacco meld to create a medium body and lightly oaked red wine
            that's perfect for settling into a relaxing evening."
         />
    );
    }


function Modal(props) {
   return(
            <div class="plus-block--item-wrapper inline" onClick={ShowModal}>
                <div class="plus-block--img-wrapper">
                    <img src={props.image_source}></img>
                        <h3>{props.name}</h3>
                            <div class="modal fade" id={props.id} tabindex="-1" role="dialog" aria-hidden="true">
                                <div class="modal-dialog" role="document">
                                    <div class="modal-content">
                                        <ModalHeader name={props.name}/>
                                            <ModalBody text={props.modal_text}/>
                                    </div>
                                </div>
                            </div>
                </div>
            </div>
  );
}


function ModalHeader(props) {
    return (
        <div class="modal-header">
            <h5 class="modal-title">{props.name}</h5>
                <button type="button" class="close" onClick={HideModal} aria-label="Close">
            <span aria-hidden="true">&times;</span>
            </button>
        </div>
    );
}


function ModalBody(props) {
   return(
      <div class="modal-body">
         <p>{props.text}
         </p>
    </div>
   );
}


function ShowModal(props) {
    return(
        $("#cabernet-modal").modal('show')
    );
}


function HideModal(props) {
    return(
        $('#cabernet-modal').modal('hide')
    );
}


const domContainer = document.querySelector('#modal_container');
ReactDOM.render(
    <CabernetModal />, domContainer
);