import React, { useState, useEffect, useRef } from 'react';
import { useGeminiSocket } from './useGeminiSocket';

const SEQUENCE_LENGTH = 4;
const ROUND_TIME = 60;

const generateSequence = () => {
    const nums = new Set();
    while (nums.size < SEQUENCE_LENGTH) {
        nums.add(Math.floor(Math.random() * 5) + 1); // 1-5
    }
    return Array.from(nums);
};

export default function BiometricLock() {
    const [sequence, setSequence] = useState([]);
    const [inputProgress, setInputProgress] = useState([]);
    const [status, setStatus] = useState('IDLE'); // IDLE, SCANNING, SUCCESS, FAIL
    const [timeLeft, setTimeLeft] = useState(ROUND_TIME);

    const videoRef = useRef(null);
    // ADK backend expects /ws/{user_id}/{session_id}
    // Generate random session ID on mount to ensure fresh session
    const sessionId = useRef(Math.random().toString(36).substring(7)).current;
    const { status: socketStatus, lastMessage, connect, disconnect, startStream, stopStream } = useGeminiSocket(`ws://localhost:8080/ws/user1/${sessionId}`);

    // Handle Game Start
    const startRound = () => {
        const newSeq = generateSequence();
        setSequence(newSeq);
        setInputProgress([]);
        setTimeLeft(ROUND_TIME);
        setStatus('SCANNING');

        // Connect and start stream if not already
        connect();
    };

    useEffect(() => {
        if (status === 'SCANNING') {
            startStream(videoRef.current);
        } else if (status === 'SUCCESS' || status === 'FAIL') {
            stopStream();
            disconnect();
        }
    }, [status, startStream, stopStream, disconnect]);

    // Timer
    useEffect(() => {
        let interval;
        if (status === 'SCANNING') {
            interval = setInterval(() => {
                setTimeLeft((t) => {
                    if (t <= 1) {
                        setStatus('FAIL');
                        return 0;
                    }
                    return t - 1;
                });
            }, 1000);
        }
        return () => clearInterval(interval);
    }, [status]);

    // Game Logic - Input Handling
    useEffect(() => {
        if (status !== 'SCANNING' || !lastMessage) return;

        if (lastMessage.type === 'DIGIT_DETECTED') {
            const detected = lastMessage.value;
            const targetIndex = inputProgress.length;
            const targetValue = sequence[targetIndex];

            if (detected === targetValue) {
                const newProgress = [...inputProgress, detected];
                setInputProgress(newProgress);

                if (newProgress.length === SEQUENCE_LENGTH) {
                    setStatus('SUCCESS');
                }
            }
        }
    }, [lastMessage, status, sequence, inputProgress]);

    return (
        <div className="relative w-full h-screen bg-black overflow-hidden font-mono text-neon-cyan select-none">
            {/* Background Video */}
            <video
                ref={videoRef}
                muted
                playsInline
                className={`absolute top-0 left-0 w-full h-full object-cover z-0 opacity-50 grayscale transition-all duration-1000 ${status === 'SUCCESS' ? 'grayscale-0 opacity-100 blur-sm' :
                    status === 'FAIL' ? 'grayscale opacity-20 blur-md' : ''
                    }`}
            />

            {/* Scanlines Overlay - Disable on end game for clear view */}
            {status === 'SCANNING' && <div className="scanlines z-10"></div>}

            {/* Success/Fail Overlays with Dynamic Effects */}
            {status === 'SUCCESS' && (
                <div className="absolute inset-0 z-30 flex items-center justify-center bg-green-900/40 backdrop-blur-sm animate-fade-in">
                    <div className="text-center">
                        <h1 className="text-8xl font-black text-white drop-shadow-[0_0_30px_rgba(0,255,0,0.8)] animate-bounce">
                            ACCESS GRANTED
                        </h1>
                        <p className="text-2xl text-neon-green mt-4 tracking-[1em] animate-pulse">
                            SYSTEM UNLOCKED
                        </p>
                        <button
                            onClick={startRound}
                            className="mt-12 px-8 py-3 bg-black/80 border border-neon-green text-neon-green hover:bg-neon-green hover:text-black transition-all"
                        >
                            REBOOT SYSTEM
                        </button>
                    </div>
                    {/* Confetti-like particles (simple CSS circles) */}
                    <div className="absolute inset-0 pointer-events-none overflow-hidden">
                        {[...Array(20)].map((_, i) => (
                            <div key={i} className="absolute w-2 h-2 bg-neon-green rounded-full animate-ping"
                                style={{
                                    left: `${Math.random() * 100}%`,
                                    top: `${Math.random() * 100}%`,
                                    animationDuration: `${Math.random() * 2 + 1}s`
                                }}
                            />
                        ))}
                    </div>
                </div>
            )}

            {status === 'FAIL' && (
                <div className="absolute inset-0 z-30 flex items-center justify-center bg-red-900/60 backdrop-blur-sm animate-shake">
                    <div className="text-center">
                        <h1 className="text-9xl font-black text-red-600 drop-shadow-[0_0_50px_rgba(255,0,0,1)] glitch-text">
                            CRITICAL FAIL
                        </h1>
                        <p className="text-3xl text-red-400 mt-4 tracking-widest uppercase font-bold">
                            Time Expired / Protocol Breach
                        </p>
                        <button
                            onClick={startRound}
                            className="mt-12 px-8 py-3 bg-black/80 border border-red-500 text-red-500 hover:bg-red-500 hover:text-black transition-all"
                        >
                            RETRY SEQUENCE
                        </button>
                    </div>
                </div>
            )}

            {/* Main HUD */}
            <div className={`relative z-20 flex flex-col items-center justify-between h-full py-10 px-4 transition-opacity duration-500 ${status !== 'SCANNING' && status !== 'IDLE' ? 'opacity-20 blur-sm' : 'opacity-100'}`}>

                {/* Header */}
                <div className="w-full max-w-4xl flex justify-between items-center border-b-2 border-neon-cyan/50 pb-4 bg-black/60 backdrop-blur-sm p-6 rounded-t-xl">
                    <div>
                        <h1 className="text-2xl font-bold tracking-widest text-glow">SECURITY PROTOCOL: LEVEL 5</h1>
                        <div className="text-xs text-neon-cyan/70">Bio-Signature Required</div>
                    </div>
                    <div className={`px-4 py-2 text-xl font-bold border ${Math.random() > 0.5 ? 'animate-pulse' : ''} ${status === 'IDLE' ? 'border-red-500 text-red-500' :
                        status === 'SCANNING' ? 'border-yellow-400 text-yellow-400' : ''
                        }`}>
                        {status === 'IDLE' && 'LOCKED'}
                        {status === 'SCANNING' && 'OVERRIDE IN PROGRESS'}
                    </div>
                </div>

                {/* Center Challenge */}
                <div className="flex-1 flex flex-col items-center justify-center gap-12 w-full max-w-4xl">

                    {status === 'IDLE' && (
                        <button
                            onClick={startRound}
                            className="px-12 py-6 text-2xl font-bold border-2 border-neon-cyan hover:bg-neon-cyan hover:text-black transition-all shadow-[0_0_20px_rgba(0,255,255,0.3)] animate-pulse"
                        >
                            INITIATE OVERRIDE
                        </button>
                    )}

                    {status === 'SCANNING' && (
                        <>
                            {/* The Sequence */}
                            <div className="flex gap-6">
                                {sequence.map((num, idx) => {
                                    const isMatched = idx < inputProgress.length;
                                    return (
                                        <div key={idx} className={`w-24 h-32 flex items-center justify-center text-6xl font-bold border-4 rounded-lg transition-all duration-300 ${isMatched
                                            ? 'border-neon-green text-neon-green bg-neon-green/10 shadow-[0_0_30px_rgba(0,255,65,0.5)] transform scale-110'
                                            : 'border-neon-cyan text-neon-cyan bg-black/50 shadow-[0_0_15px_rgba(0,255,255,0.2)] animate-pulse-fast'
                                            }`}>
                                            {num}
                                        </div>
                                    )
                                })}
                            </div>

                            {/* Feedback Slots */}
                            <div className="flex gap-6 opacity-80">
                                {Array(SEQUENCE_LENGTH).fill(0).map((_, idx) => {
                                    const isFilled = idx < inputProgress.length;
                                    const isCurrent = idx === inputProgress.length;
                                    return (
                                        <div key={idx} className={`w-24 h-4 border-b-4 transition-all ${isFilled ? 'border-neon-green' :
                                            isCurrent ? 'border-white animate-pulse' : 'border-gray-700'
                                            }`}></div>
                                    )
                                })}
                            </div>
                        </>
                    )}
                </div>

                {/* Footer / Timer */}
                <div className="w-full max-w-4xl grid grid-cols-3 items-end">
                    <div className="text-xl">
                        SINGLE STAGE OPERATION
                    </div>

                    <div className="flex justify-center">
                        {status === 'SCANNING' && (
                            <div className={`text-6xl font-black tabular-nums tracking-tighter ${timeLeft <= 10 ? 'text-red-500 animate-bounce' : 'text-white'}`}>
                                00:{timeLeft.toString().padStart(2, '0')}
                            </div>
                        )}
                    </div>

                    <div className="text-right text-xl">
                        STATUS: {socketStatus}
                    </div>
                </div>

            </div>
        </div>
    );
}
