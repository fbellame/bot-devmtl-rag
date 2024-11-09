from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.vectorstores.base import VectorStore
from langchain.chains.base import Chain
from langchain.schema import Document
from typing import List, Dict, Any
from langchain_community.document_compressors.flashrank_rerank import FlashrankRerank

# FUNCTION TO INITIALIZE AND RETURN AN INSTANCE OF THE CHAIN
def get_chain(vectorstore: VectorStore):
    retriever = vectorstore.as_retriever(score_threshold = .7)
    template = """Réponds à la question de manière succinte en utilisant le contexte suivant, si la question est en anglais répond en anglais:
{context}

Question: {question}
Réponse (avec références):"""
    prompt = ChatPromptTemplate.from_template(template)
    model = ChatOpenAI(model_name="gpt-4o-mini")
    
    # Initialize compressor with top_n parameter
    compressor = FlashrankRerank(top_n=3)
    chain = RetrievalWithCitationsChain(retriever=retriever, model=model, prompt=prompt, compressor = compressor)
    
    return chain

class RetrievalWithCitationsChain(Chain):
    retriever: Any
    model: Any
    prompt: ChatPromptTemplate
    compressor: FlashrankRerank
    
    def _call(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        question = inputs["question"]
                
        # RETRIEVE RELEVANT DOCUMENTS USING THE RETRIEVER
        retrieved_docs: List[Document] = self.retriever.invoke(question)
        compressed_docs = self.compressor.compress_documents(retrieved_docs, question)
        
        # Build context
        context = "\n".join([doc.page_content for doc in compressed_docs])

        # Format prompt
        prompt_input = self.prompt.format(context=context.strip(), question=question)
        # Get model response
        response = self.model.invoke(prompt_input)
        answer = response.content if hasattr(response, 'content') else str(response)

        # RETURN THE ANSWER AND THE RETRIEVED DOCUMENTS USED FOR CONTEXT
        return {
            "answer": answer,
            "retrieved_docs": compressed_docs
        }

    @property
    def input_keys(self) -> List[str]:
        return ["question"]

    @property
    def output_keys(self) -> List[str]:
        return ["answer"]