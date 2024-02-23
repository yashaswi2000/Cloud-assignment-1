import { LexRuntimeV2Client, RecognizeTextCommand } from "@aws-sdk/client-lex-runtime-v2"; // ES Modules import
const client = new LexRuntimeV2Client({ region: "us-east-1" });

export const handler = async (event) => {
  
  if (event.messages) {
      const input = { // RecognizeTextRequest
      botId: "C79NLJ913W", // required
      botAliasId: "TSTALIASID", // required
      localeId: "en_US", // required
      sessionId: "temp_session",
      text: event.messages[0].unstructured.text, // required
    };
  const command = new RecognizeTextCommand(input);
  const botresponse = await client.send(command);
  console.log(botresponse);
  
  const response = {
    statusCode: 200,
    messages: [
        {
          type: "unstructured",
          unstructured: {
           id: "temp",
           text: botresponse.messages[0].content,
           timestamp: Date.now()
          }
        }
      ]
    ,
  };
  return response;
  
    
  }  
};
