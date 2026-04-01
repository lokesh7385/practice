package com.experement.accountability.ai

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONObject
import java.util.concurrent.TimeUnit

class AiAgentHandler(private val apiKey: String) {

    private val client = OkHttpClient.Builder()
        .connectTimeout(5, TimeUnit.SECONDS)
        .readTimeout(8, TimeUnit.SECONDS)
        .build()

    private val systemPrompt = """
        You are The Gatekeeper. The user wants to open a distracting app.
        They must provide a LEGITIMATE, SPECIFIC reason.
        
        Rules:
        - "I'm bored" → DENIED
        - "Just checking" → DENIED  
        - "I need to reply to a DM from [specific person] about [specific topic]" → APPROVED
        - "I need to watch a tutorial on [specific skill]" → APPROVED
        - Set a time limit suggestion (5-15 min) for approved requests.
        
        Respond EXACTLY in this format:
        VERDICT: APPROVED|DENIED
        REASON: <one sentence>
        TIME_LIMIT: <minutes, only if APPROVED>
    """.trimIndent()

    suspend fun judge(appName: String, justification: String): AiVerdict = withContext(Dispatchers.IO) {
        try {
            val body = JSONObject().apply {
                put("contents", JSONArray().apply {
                    put(JSONObject().apply {
                        put("role", "user")
                        put("parts", JSONArray().apply {
                            put(JSONObject().apply {
                                put("text", "App: $appName\nJustification: $justification")
                            })
                        })
                    })
                })
                put("systemInstruction", JSONObject().apply {
                    put("parts", JSONArray().apply {
                        put(JSONObject().apply {
                            put("text", systemPrompt)
                        })
                    })
                })
            }

            val request = Request.Builder()
                .url("https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=$apiKey")
                .post(body.toString().toRequestBody("application/json".toMediaType()))
                .build()

            val response = client.newCall(request).execute()
            val responseString = response.body?.string() ?: ""
            if (!response.isSuccessful) {
                return@withContext AiVerdict.Denied("API Error: ${response.code}")
            }
            parseVerdict(responseString)
        } catch (e: Exception) {
            e.printStackTrace()
            AiVerdict.Denied("Network error. Access denied by default.")
        }
    }

    private fun parseVerdict(raw: String): AiVerdict {
        return try {
            val text = JSONObject(raw)
                .getJSONArray("candidates")
                .getJSONObject(0)
                .getJSONObject("content")
                .getJSONArray("parts")
                .getJSONObject(0)
                .getString("text")

            when {
                "VERDICT: APPROVED" in text -> {
                    val timeLimit = Regex("""TIME_LIMIT:\s*(\d+)""")
                        .find(text)?.groupValues?.get(1)?.toIntOrNull() ?: 10
                    val reason = Regex("""REASON:\s*(.+)""").find(text)?.groupValues?.get(1) ?: "Approved."
                    AiVerdict.Approved(reason, timeLimit)
                }
                else -> {
                    val reason = Regex("""REASON:\s*(.+)""").find(text)?.groupValues?.get(1) ?: "Request denied."
                    AiVerdict.Denied(reason)
                }
            }
        } catch (e: Exception) {
            AiVerdict.Denied("Failed to parse AI response.")
        }
    }
}
