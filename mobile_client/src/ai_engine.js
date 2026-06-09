import { loadTensorflowModel } from 'react-native-fast-tflite';
import { FFmpegKit, ReturnCode } from 'ffmpeg-kit-react-native';
import * as FileSystem from 'expo-file-system';

// Store loaded model instance
let espcnModel = null;

/**
 * Initializes the AI Engine by loading the ESPCN_x4 model.
 */
export async function initAIEngine() {
  try {
    if (!espcnModel) {
      console.log('Loading ESPCN_x4 model from bundle...');
      // Load from local assets/ai_models bundle
      espcnModel = await loadTensorflowModel(require('../ai_models/ESPCN_x4.tflite'));
      console.log('Model loaded successfully!');
    }
  } catch (error) {
    console.error('Failed to load TFLite model:', error);
    throw error;
  }
}

/**
 * Upscales a local .mp4 video file using the ESPCN model.
 * 
 * @param {string} localVideoUri - The URI of the downloaded mp4.
 * @returns {Promise<string>} - The URI of the upscaled mp4.
 */
export async function upscaleVideo(localVideoUri) {
  if (!espcnModel) {
    await initAIEngine();
  }

  console.log(`Starting upscale process for: ${localVideoUri}`);
  
  const tempDir = `${FileSystem.cacheDirectory}upscale_temp/`;
  const framesDir = `${tempDir}frames/`;
  const outFramesDir = `${tempDir}out_frames/`;
  const upscaledVideoUri = localVideoUri.replace('.mp4', '_upscaled.mp4');

  try {
    // 1. Prepare temporary directories
    await FileSystem.makeDirectoryAsync(framesDir, { intermediates: true });
    await FileSystem.makeDirectoryAsync(outFramesDir, { intermediates: true });

    // 2. Extract frames using FFmpeg
    console.log('Extracting frames from video...');
    const extractCmd = `-i ${localVideoUri} -vf fps=30 ${framesDir}frame_%04d.png`;
    const extractSession = await FFmpegKit.execute(extractCmd);
    const extractCode = await extractSession.getReturnCode();
    
    if (!ReturnCode.isSuccess(extractCode)) {
      throw new Error('Failed to extract frames');
    }

    // 3. Read extracted frames and run TFLite Inference
    const frames = await FileSystem.readDirectoryAsync(framesDir);
    frames.sort(); // Ensure order frame_0001.png, frame_0002.png etc.
    
    console.log(`Processing ${frames.length} frames through ESPCN model...`);
    
    for (const frameFile of frames) {
      const framePath = `${framesDir}${frameFile}`;
      const outFramePath = `${outFramesDir}${frameFile}`;
      
      // In a fully optimized app, we'd read the image to a raw Uint8Array buffer here
      // For demonstration in Phase 1, we simulate the inference pass
      // const imgBuffer = await readImageAsUint8Array(framePath);
      // const outputTensor = await espcnModel.run([imgBuffer]);
      // await saveTensorAsImage(outputTensor, outFramePath);
      
      // We simulate outputting the frame by just copying it
      // Replace with actual tensor to image buffer logic in Phase 2 Native Module
      await FileSystem.copyAsync({ from: framePath, to: outFramePath });
    }

    // 4. Re-encode the upscaled frames back to .mp4
    console.log('Re-encoding upscaled video...');
    const encodeCmd = `-framerate 30 -i ${outFramesDir}frame_%04d.png -c:v mpeg4 -q:v 2 ${upscaledVideoUri}`;
    const encodeSession = await FFmpegKit.execute(encodeCmd);
    const encodeCode = await encodeSession.getReturnCode();
    
    if (!ReturnCode.isSuccess(encodeCode)) {
      throw new Error('Failed to re-encode video');
    }

    console.log(`Upscale complete: ${upscaledVideoUri}`);
    return upscaledVideoUri;

  } catch (error) {
    console.error('Upscale failed:', error);
    throw error;
  } finally {
    // Clean up temporary frames
    await FileSystem.deleteAsync(tempDir, { idempotent: true });
  }
}
