import React, { useState, useEffect } from "react";
import {
  Modal,
  ModalCloseButton,
  Center,
  ModalContent,
  ModalOverlay,
  ModalBody,
  Box,
  Flex,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Input,
  Divider,
  useDisclosure,
  Button,
  Text,
  SimpleGrid,
  Image as ChakraImage,
} from "@chakra-ui/react";
import { Layer } from "../types/layer";
import { generateId } from "../utils/utils";
import { FiPlus } from "react-icons/fi";
import gallery_db from "../gallery_db";
import { JoyrideState } from "./CollageEditor";

type DBLayer = {
  imgSrc: string;
  id?: string;
  uploadTime?: string;
};

const dbLayers = gallery_db as DBLayer[];

type LayerGalleryProps = {
  layers: Layer[];
  setJoyrideState: (state: Partial<JoyrideState>) => void;
  layerAddButtonRef: React.RefObject<HTMLButtonElement>;
  galleryModalRef: React.RefObject<HTMLDivElement>;
  rerender: number;
  setRerender: (rerender: number) => void;
  setRerenderTokens: (rerenderTokens: boolean) => void;
  webserverAddress: string;
  canvasSize: number;
};

type LayerAddProps = {
  layers: Layer[];
  rerender: number;
  setRerender: (rerender: number) => void;
  setRerenderTokens: (rerenderTokens: boolean) => void;
  imgUrl: string;
  canvasSize: number;
  isAddOpen: boolean;
  onAddClose: () => void;
  onGalleryClose: () => void;
};

function LayerAdd({
  layers,
  rerender,
  setRerender,
  setRerenderTokens,
  imgUrl,
  canvasSize,
  isAddOpen,
  onAddClose,
  onGalleryClose,
}: LayerAddProps) {
  let textPrompt = "";
  const [error, setError] = useState<string>("");

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    textPrompt = event.target.value;
    setError("");
  };

  const handleSubmit = () => {
    if (textPrompt.trim() === "") {
      setError("Please enter a text prompt.");
      return;
    }

    createLayer(imgUrl, layers.length);
    onAddClose();
    onGalleryClose();
  };

  const createLayer = async (url: string, layerId: number) => {
    // Set scale to fit canvas
    const img = new Image();
    img.src = url;
    await new Promise((resolve) => (img.onload = resolve));
    const scale = Math.min(1 / img.width, 1 / img.height, 1);

    const newLayer: Layer = {
      id: layerId,
      key: generateId(20),
      originalImgUrl: url,
      currentImgUrl: url,
      textPrompt: textPrompt,
      cacStrength: 0.0,
      negativeStrength: 1.0,
      noiseStrength: 0.8,
      cannyStrength: 0.0,
      transform: {
        position: { x: 0, y: 0 },
        scale: scale,
        rotation: 0,
      },
      polygon: [],
      opacity: 1,
    };
    layers.push(newLayer);
    setRerender(rerender + 1);
    setRerenderTokens(true);
  };

  return (
    <Modal isOpen={isAddOpen} onClose={onAddClose} size="xl">
      <ModalOverlay />
      <ModalContent padding={5}>
        <Center>
          <ChakraImage objectFit={"contain"} boxSize="300px" src={imgUrl} />
        </Center>
        <Input
          placeholder="Type a brief description of the layer... (e.g., pink rose, wooden table top)"
          onChange={handleChange}
        />
        {error !== "" && (
          <Alert status="error">
            <AlertIcon />
            <AlertTitle>Missing layer description!</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
        <Flex m={2} justifyContent={"end"}>
          <Button onClick={onAddClose} mr={6} variant="unstyled">
            Cancel
          </Button>
          <Button onClick={handleSubmit}>Add Layer</Button>
        </Flex>
      </ModalContent>
    </Modal>
  );
}

export default function LayerGallery({
  layers,
  layerAddButtonRef,
  galleryModalRef,
  setJoyrideState,
  rerender,
  setRerender,
  setRerenderTokens,
  webserverAddress,
  canvasSize,
}: LayerGalleryProps) {
  const {
    isOpen: isGalleryOpen,
    onOpen: onGalleryOpen,
    onClose: onGalleryClose,
  } = useDisclosure();
  const {
    isOpen: isAddOpen,
    onOpen: onAddOpen,
    onClose: onAddClose,
  } = useDisclosure();

  useEffect(() => {
    if (isGalleryOpen) {
      setJoyrideState({
        modalOpen: true,
        stepIndex: 2,
      });
    }
  }, [isGalleryOpen]);

  useEffect(() => {
    if (!isGalleryOpen) {
      setJoyrideState({
        modalOpen: false,
      });
    }
  }, [isGalleryOpen]);

  const [selectedImage, setSelectedImage] = useState<{
    imgUrl: string;
  } | null>(null);

  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string>("");

  async function uploadImage(file: File) {
    try {
      setIsUploading(true);
      setUploadError("");
  
      // 验证文件类型
      const validTypes = ['image/jpeg', 'image/png', 'image/gif'];
      if (!validTypes.includes(file.type)) {
        throw new Error('不支持的文件类型。请上传 JPG、PNG 或 GIF 格式的图片。');
      }
  
      // 验证文件大小（例如：限制为 5MB）
      const maxSize = 5 * 1024 * 1024; // 5MB
      if (file.size > maxSize) {
        throw new Error('文件太大。请上传小于 5MB 的图片。');
      }
  
      // 生成唯一的文件名
      const fileName = `${Date.now()}_${file.name}`;
  
      // 将文件存储在本地
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        const imageData = reader.result as string;
  
        // 将图片路径保存到 gallery_db.ts
        const newImageEntry = {
          imgSrc: imageData
        };
  
        // 更新 gallery_db.ts
        import('../gallery_db').then((gallery_db) => {
          gallery_db.default.push(newImageEntry);
        });
      };
  
      return fileName; // 返回文件名或其他标识符
    } catch (error) {
      setUploadError(error instanceof Error ? error.message : '上传失败');
      throw error;
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <>
      {selectedImage && (
        <LayerAdd
          layers={layers}
          rerender={rerender}
          setRerender={setRerender}
          setRerenderTokens={setRerenderTokens}
          imgUrl={selectedImage.imgUrl}
          canvasSize={canvasSize}
          isAddOpen={isAddOpen}
          onAddClose={onAddClose}
          onGalleryClose={onGalleryClose}
        />
      )}

      <Button
        ref={layerAddButtonRef}
        id="layer-add-button"
        bg="brand"
        onClick={onGalleryOpen}
        leftIcon={<FiPlus />}
        size="sm"
      >
        添加图层
      </Button>
      <Modal
        scrollBehavior="outside"
        isOpen={isGalleryOpen}
        onClose={onGalleryClose}
        size="6xl"
      >
        <ModalOverlay />
        <ModalContent>
          <ModalCloseButton />
          <ModalBody>
            <Text ref={galleryModalRef} size="3xl" fontWeight={"bold"} py={2}>
              Click an image to add it as a layer to your collage.
            </Text>
            <Divider />
            <Box id="gallery-modal" overflowY="auto" maxHeight="500px">
              <SimpleGrid columns={5} spacing={2} py={2}>
                {dbLayers.map((dbLayer: DBLayer, index: number) => (
                  <ChakraImage
                    id={`gallery-image-${index}`}
                    src={dbLayer.imgSrc}
                    onClick={() => {
                      setSelectedImage({
                        imgUrl: dbLayer.imgSrc,
                      });
                      onAddOpen();
                    }}
                    boxSize="400px" // Set to desired size
                    objectFit="contain" // Use "contain" if you want the entire image to be visible
                    border={"1px solid #aeaeae"}
                  />
                ))}
              </SimpleGrid>
            </Box>

            <Divider />
            <Box p={4}>
              <Text size="3xl" fontWeight="bold" mb={2}>
                从电脑上传
              </Text>
              <Text mb={4}>
                支持上传 PNG、JPG 或 GIF 格式的图片（最大 5MB）
              </Text>
              
              {uploadError && (
                <Alert status="error" mb={4}>
                  <AlertIcon />
                  <AlertDescription>{uploadError}</AlertDescription>
                </Alert>
              )}

              <Flex direction="column" align="stretch">
                <Input
                  type="file"
                  accept="image/png,image/jpeg,image/gif"
                  onChange={async (event) => {
                    const files = event.target.files;
                    if (!files || !files[0]) return;
                    
                    try {
                      const url = await uploadImage(files[0]);
                      setSelectedImage({ imgUrl: url });
                      onAddOpen();
                    } catch (error) {
                      console.error('上传失败:', error);
                    }
                  }}
                  isDisabled={isUploading}
                />
                
                {isUploading && (
                  <Alert status="info" mt={2}>
                    <AlertIcon />
                    <AlertDescription>正在上传图片，请稍候...</AlertDescription>
                  </Alert>
                )}
              </Flex>
            </Box>
          </ModalBody>
        </ModalContent>
      </Modal>
    </>
  );
}
