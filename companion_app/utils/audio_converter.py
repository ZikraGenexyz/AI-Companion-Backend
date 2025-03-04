from pydub import AudioSegment
import os
import logging
from typing import Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_mp4_to_wav(
    input_path: str,
    output_path: Optional[str] = None,
    sample_rate: int = 16000,
    channels: int = 1,
    sample_width: int = 2
) -> Tuple[bool, str]:
    """
    Convert an MP4 file to WAV format.
    
    Args:
        input_path (str): Path to the input MP4 file
        output_path (str, optional): Path for the output WAV file. If not provided,
                                   will use the same name as input with .wav extension
        sample_rate (int): Output sample rate in Hz (default: 16000)
        channels (int): Number of audio channels (default: 1 for mono)
        sample_width (int): Sample width in bytes (default: 2 for 16-bit)
    
    Returns:
        Tuple[bool, str]: (Success status, Message)
    """
    try:
        # Validate input file
        if not os.path.exists(input_path):
            return False, f"Input file not found: {input_path}"
        
        if not input_path.lower().endswith('.mp4'):
            return False, "Input file must be an MP4 file"
        
        # Generate output path if not provided
        if output_path is None:
            output_path = os.path.splitext(input_path)[0] + '.wav'
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        logger.info(f"Converting {input_path} to WAV format...")
        
        # Load the MP4 file
        audio = AudioSegment.from_file(input_path, format="mp4")
        
        # Convert to desired format
        audio = audio.set_channels(channels)
        audio = audio.set_frame_rate(sample_rate)
        audio = audio.set_sample_width(sample_width)
        
        # Export as WAV
        audio.export(output_path, format="wav")
        
        logger.info(f"Successfully converted to: {output_path}")
        return True, f"Successfully converted to: {output_path}"
        
    except Exception as e:
        error_msg = f"Error converting MP4 to WAV: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

def get_audio_info(file_path: str) -> Tuple[bool, dict]:
    """
    Get information about an audio file.
    
    Args:
        file_path (str): Path to the audio file
    
    Returns:
        Tuple[bool, dict]: (Success status, Audio information dictionary)
    """
    try:
        audio = AudioSegment.from_file(file_path)
        info = {
            "duration_ms": len(audio),
            "channels": audio.channels,
            "frame_rate": audio.frame_rate,
            "sample_width": audio.sample_width,
            "frame_width": audio.frame_width,
            "frame_count": len(audio) / (1000.0 / audio.frame_rate)
        }
        return True, info
    except Exception as e:
        return False, {"error": str(e)}

if __name__ == "__main__":
    # Example usage
    input_file = "test_file.mp4"  # Place your MP4 file in the same directory as this script
    output_file = "test_audio.wav"  # Output will be in the same directory
    
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create full paths
    input_path = os.path.join(current_dir, input_file)
    output_path = os.path.join(current_dir, output_file)
    
    success, message = convert_mp4_to_wav(input_path, output_path)
    if success:
        print(message)
        # Get audio information
        success, info = get_audio_info(output_path)
        if success:
            print("\nAudio Information:")
            for key, value in info.items():
                print(f"{key}: {value}")
    else:
        print(f"Error: {message}") 