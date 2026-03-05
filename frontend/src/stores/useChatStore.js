import { create } from 'zustand';

const useChatStore = create((set, get) => ({
    // Conversation list
    conversations: [],
    currentConversationId: null,

    // Messages in current conversation
    messages: [],
    isTyping: false,

    // Emotion state (client-side, synced with backend on each response)
    emotionState: {
        conversationTurns: 0,
        valenceHistory: [],
        arousalHistory: [],
        avgValence: 5.0,
        avgArousal: 5.0,
        meditationDone: false,
    },

    // UI state
    suggestMeditation: false,
    showMeditationModal: false,

    // Generated images
    generatedImages: [], // array of base64 strings
    selectedImageIndex: null,
    showImagePanel: false,

    // Actions
    setConversations: (convs) => set({ conversations: convs }),

    setCurrentConversation: (id) => set({
        currentConversationId: id,
        messages: [],
        generatedImages: [],
        selectedImageIndex: null,
        showImagePanel: false,
        suggestMeditation: false,
        emotionState: {
            conversationTurns: 0,
            valenceHistory: [],
            arousalHistory: [],
            avgValence: 5.0,
            avgArousal: 5.0,
            meditationDone: false,
        },
    }),

    addMessage: (msg) => set((state) => ({ messages: [...state.messages, msg] })),
    setMessages: (msgs) => set({ messages: msgs }),
    setTyping: (val) => set({ isTyping: val }),

    applyEmotionResponse: (resp) => set({
        emotionState: {
            conversationTurns: resp.conversation_turns,
            valenceHistory: resp.valence_history,
            arousalHistory: resp.arousal_history,
            avgValence: resp.avg_valence,
            avgArousal: resp.avg_arousal,
            meditationDone: resp.meditation_done,
        },
        suggestMeditation: resp.suggest_meditation,
        showMeditationModal: resp.suggest_meditation,
        currentConversationId: resp.conversation_id,
    }),

    setGeneratedImages: (imgs) => set({ generatedImages: imgs, showImagePanel: true, selectedImageIndex: 0 }),
    setSelectedImage: (idx) => set({ selectedImageIndex: idx }),

    dismissMeditationModal: () => set({ showMeditationModal: false, suggestMeditation: false }),

    markMeditationDone: () => set((state) => ({
        showMeditationModal: false,
        emotionState: { ...state.emotionState, meditationDone: true },
    })),
}));

export default useChatStore;
