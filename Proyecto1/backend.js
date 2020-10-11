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

   //Aquí metemos el código de encender la luz
   // Creamos un proceso hijo 
   var exec = require('child_process').exec, child;
   // Le pasamos el comando a ejecutar (en mi casa queda mejor 222222 porque sino deslumbra mucho por la noche)
   child = exec('hyperion-remote --color FFFFFF',
   // Y la función que manejará los flujos
     function (error, stdout, stderr) {
       // Sacamos por pantalla la salida
       console.log(stdout);
       // Y también el texto de error
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

   //Aquí metemos el código de encender la luz
   // Creamos un proceso hijo 
   var exec = require('child_process').exec, child;
   // Le pasamos el comando a ejecutar
   child = exec('hyperion-remote --clearall',
   // Y la función que manejará los flujos
     function (error, stdout, stderr) {
       // Sacamos por pantalla la salida
       console.log(stdout);
       // Y también el texto de error
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
    const speechText = 'Adiós';

    return handlerInput.responseBuilder
      .speak(speechText)
      .withSimpleCard('Adiós', speechText)
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

