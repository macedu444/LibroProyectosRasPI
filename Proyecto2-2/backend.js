const Alexa = require('ask-sdk-core');

const express = require('express');
const { ExpressAdapter } = require('ask-sdk-express-adapter');

const LaunchRequestHandler = {
  canHandle(handlerInput) {
    return handlerInput.requestEnvelope.request.type === 'LaunchRequest';
  },
  handle(handlerInput) {
    const speechText = 'Raspberry escuchando';

    return handlerInput.responseBuilder
      .speak(speechText)
      .reprompt(speechText)
      .withSimpleCard('Raspberry escuchando', speechText)
      .getResponse();
  }
};

const PonAmbienteIntentHandler = {
  canHandle(handlerInput) {
    return handlerInput.requestEnvelope.request.type === 'IntentRequest'
      && handlerInput.requestEnvelope.request.intent.name === 'PonAmbienteIntent';
  },
  handle(handlerInput) {
    const speechText = 'Ambiente activado';

   //Aqu� metemos el c�digo de encender la luz
   // Creamos un proceso hijo 
   var exec = require('child_process').exec, child;
   // Le pasamos el comando a ejecutar (en mi casa queda mejor 222222 porque sino deslumbra mucho por la noche)
   child = exec('hyperion-remote --color FFFFFF',
   // Y la funci�n que manejar� los flujos
     function (error, stdout, stderr) {
       // Sacamos por pantalla la salida
       console.log(stdout);
       // Y tambi�n el texto de error
       if (error !== null) {
         console.log('exec error: ' + error);
       }
   });

  //Y finalmente respondemos

    return handlerInput.responseBuilder
      .speak(speechText)
      .withSimpleCard('Ambiente activado', speechText)
      .getResponse();
  }
};

const QuitaAmbienteIntentHandler = {
  canHandle(handlerInput) {
    return handlerInput.requestEnvelope.request.type === 'IntentRequest'
      && handlerInput.requestEnvelope.request.intent.name === 'QuitaAmbienteIntent';
  },
  handle(handlerInput) {
    const speechText = 'Ambiente desactivado';

   //Aqu� metemos el c�digo de encender la luz
   // Creamos un proceso hijo 
   var exec = require('child_process').exec, child;
   // Le pasamos el comando a ejecutar
   child = exec('hyperion-remote --clearall',
   // Y la funci�n que manejar� los flujos
     function (error, stdout, stderr) {
       // Sacamos por pantalla la salida
       console.log(stdout);
       // Y tambi�n el texto de error
       if (error !== null) {
         console.log('exec error: ' + error);
       }
   });

  //Y finalmente respondemos

    return handlerInput.responseBuilder
      .speak(speechText)
      .withSimpleCard('Ambiente desactivado', speechText)
      .getResponse();
  }
};

const ApagaTelevisionIntentHandler = {
  canHandle(handlerInput) {
    return handlerInput.requestEnvelope.request.type === 'IntentRequest'
      && handlerInput.requestEnvelope.request.intent.name === 'ApagaTelevisionIntent';
  },
  handle(handlerInput) {
    const speechText = 'Apagando televisi�n';

   // Creamos un proceso hijo
   var exec = require('child_process').exec, child;
   // Le pasamos el comando a ejecutar
   child = exec('irsend SEND_ONCE televisor BTN_0',
   // Y la funci�n que manejar� los flujos
     function (error, stdout, stderr) {
       // Sacamos por pantalla la salida
       console.log(stdout);
       // Y tambien el texto de error
       if (error !== null) {
         console.log('exec error: ' + error);
       }
   });

    //Y finalmente respondemos
    return handlerInput.responseBuilder
      .speak(speechText)
      .withSimpleCard('Infrarrojo', speechText)
      .getResponse();
  }
};

const PonCancionIntentHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'PonCancionIntent';
    },
    handle(handlerInput) {
        const nombre = handlerInput.requestEnvelope.request.intent.slots.titulo.value;
        const speakOutput = `Reproduciendo  ${nombre}`;

        console.log("Petici�n HTTP");
        //Genero la petici�n HTTP al servidor SONOS
        const http = require('http');
        const peticion = `http://192.168.1.106:5005/Sal%C3%B3n/musicsearch/library/song/${nombre}`;
        console.log(`Solicitado: ${peticion}\n`);
        let respuesta = 'error';

        http.get(peticion, (resp) => {
          let data = '';
          // Un fragmento de datos ha sido recibido.
          resp.on('data', (chunk) => {
            data += chunk;
          });

          // Toda la respuesta ha sido recibida. Imprimir el resultado (imprimo solo status).
          resp.on('end', () => {
            respuesta=JSON.parse(data).status;
            console.log(respuesta);
          });

        }).on("error", (err) => {
          console.log("Error: " + err.message);
        });
        //Fin de la petici�n HTTP

        console.log("Return de PonCancion");
        return handlerInput.responseBuilder
            .speak(speakOutput)
            .withSimpleCard('SONOS', 'Reproduciendo '+nombre)
            .getResponse();
    }
};

const HelpIntentHandler = {
  canHandle(handlerInput) {
    return handlerInput.requestEnvelope.request.type === 'IntentRequest'
      && handlerInput.requestEnvelope.request.intent.name === 'AMAZON.HelpIntent';
  },
  handle(handlerInput) {
    const speechText = 'Hola mundo';

    return handlerInput.responseBuilder
      .speak(speechText)
      .reprompt(speechText)
      .withSimpleCard('Hola mundo', speechText)
      .getResponse();
  }
};

const CancelAndStopIntentHandler = {
  canHandle(handlerInput) {
    return handlerInput.requestEnvelope.request.type === 'IntentRequest'
      && (handlerInput.requestEnvelope.request.intent.name === 'AMAZON.CancelIntent'
        || handlerInput.requestEnvelope.request.intent.name === 'AMAZON.StopIntent');
  },
  handle(handlerInput) {
    const speechText = 'Adi�s';

    return handlerInput.responseBuilder
      .speak(speechText)
      .withSimpleCard('Adi�s', speechText)
      .withShouldEndSession(true)
      .getResponse();
  }
};

const SessionEndedRequestHandler = {
  canHandle(handlerInput) {
    return handlerInput.requestEnvelope.request.type === 'SessionEndedRequest';
  },
  handle(handlerInput) {
    //any cleanup logic goes here
    return handlerInput.responseBuilder.getResponse();
  }
};

const ErrorHandler = {
  canHandle() {
    return true;
  },
  handle(handlerInput, error) {
    console.log(`Error handled: ${error.message}`);

    return handlerInput.responseBuilder
      .speak('Lo siento, no te he entendido.')
      .reprompt(' Lo siento, no te he entendido.')
      .getResponse();
  },
};


const app = express();
const skillBuilder = Alexa.SkillBuilders.custom();
const skill = skillBuilder
              .addRequestHandlers(
              LaunchRequestHandler,
              PonAmbienteIntentHandler,
              QuitaAmbienteIntentHandler,
              ApagaTelevisionIntentHandler,
              PonCancionIntentHandler,
              HelpIntentHandler,
              CancelAndStopIntentHandler,
              SessionEndedRequestHandler,
              )
              .addErrorHandlers(ErrorHandler)
              .create();
const adapter = new ExpressAdapter(skill, true, true);

app.post('/', adapter.getRequestHandlers());
app.listen(8090);

console.log("Escuchando en puerto 8090");
