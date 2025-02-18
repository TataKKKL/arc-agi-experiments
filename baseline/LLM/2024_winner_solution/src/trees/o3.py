from src.models import (
    AttemptEdge,
    FixAttemptConfig,
    FixPromptConfig,
    KTopConfig,
    LLMConfig,
    Model,
    PoolingConfig,
    Prompt,
    RootAttemptConfig,
    RootPromptConfig,
)

model = Model.o3_mini

prod_kaggle_tree: list[RootAttemptConfig] = [
    RootAttemptConfig(
        attempts=50,
        llm_config=LLMConfig(
            model=model,
            temperature=0.95,
        ),
        prompt_config=RootPromptConfig(
            base_prompt=Prompt.REASONING,
            use_examples=True,
            use_diffs=True,
            use_images=False,
            use_ascii=True,
            use_array=True,
            use_image=False,
        ),
        fixes=[],
    ),
    RootAttemptConfig(
        include_all_attempts_in_fixes=True,
        attempts=200,
        llm_config=LLMConfig(
            model=model,
            temperature=0.95,
        ),
        prompt_config=RootPromptConfig(
            base_prompt=Prompt.REASONING,
            use_examples=True,
            use_diffs=True,
            use_images=False,
            use_ascii=True,
            use_array=True,
            use_image=False,
        ),
        fixes=[
            AttemptEdge(
                k_top_config=KTopConfig(
                    k_top=10, unique_code=False, unique_output=False
                ),
                configs=[
                    FixAttemptConfig(
                        attempts=10,
                        llm_config=LLMConfig(
                            model=model,
                            temperature=0.95,
                        ),
                        prompt_config=FixPromptConfig(
                            base_prompt=Prompt.REASONING,
                            use_ascii=True,
                            use_array=True,
                            use_image=False,
                            use_fix_reasoning_tags=True,
                            use_fix_fail_line=True,
                            use_typical_issue_text=True,
                            include_diffs=True,
                        ),
                        fixes=[
                            AttemptEdge(
                                k_top_config=KTopConfig(
                                    k_top=5, unique_code=False, unique_output=False
                                ),
                                configs=[
                                    FixAttemptConfig(
                                        attempts=10,
                                        llm_config=LLMConfig(
                                            model=model,
                                            temperature=0.95,
                                        ),
                                        prompt_config=FixPromptConfig(
                                            base_prompt=Prompt.REASONING,
                                            use_ascii=True,
                                            use_array=True,
                                            use_image=False,
                                            use_fix_reasoning_tags=True,
                                            use_fix_fail_line=True,
                                            use_typical_issue_text=True,
                                            include_diffs=True,
                                        ),
                                        fixes=[
                                            AttemptEdge(
                                                k_top_config=KTopConfig(
                                                    k_top=5,
                                                    unique_code=False,
                                                    unique_output=False,
                                                ),
                                                configs=[
                                                    FixAttemptConfig(
                                                        attempts=10,
                                                        llm_config=LLMConfig(
                                                            model=model,
                                                            temperature=0.95,
                                                        ),
                                                        prompt_config=FixPromptConfig(
                                                            base_prompt=Prompt.REASONING,
                                                            use_ascii=True,
                                                            use_array=True,
                                                            use_image=False,
                                                            use_fix_reasoning_tags=True,
                                                            use_fix_fail_line=True,
                                                            use_typical_issue_text=True,
                                                            include_diffs=True,
                                                        ),
                                                        fixes=[],
                                                    )
                                                ],
                                            )
                                        ],
                                    )
                                ],
                            )
                        ],
                    )
                ],
            ),
            AttemptEdge(
                pooling=(PoolingConfig(size=3)),
                k_top_config=KTopConfig(
                    k_top=5, unique_code=False, unique_output=False
                ),
                configs=[
                    FixAttemptConfig(
                        attempts=5,
                        llm_config=LLMConfig(
                            model=model,
                            temperature=0.95,
                        ),
                        prompt_config=FixPromptConfig(
                            base_prompt=Prompt.REASONING,
                            use_ascii=True,
                            use_array=True,
                            use_image=False,
                            use_fix_reasoning_tags=True,
                            use_fix_fail_line=True,
                            use_typical_issue_text=True,
                            include_diffs=True,
                        ),
                        fixes=[
                            AttemptEdge(
                                pooling=(PoolingConfig(size=3)),
                                k_top_config=KTopConfig(
                                    k_top=5, unique_code=False, unique_output=False
                                ),
                                configs=[
                                    FixAttemptConfig(
                                        attempts=5,
                                        llm_config=LLMConfig(
                                            model=model,
                                            temperature=0.95,
                                        ),
                                        prompt_config=FixPromptConfig(
                                            base_prompt=Prompt.REASONING,
                                            use_ascii=True,
                                            use_array=True,
                                            use_image=False,
                                            use_fix_reasoning_tags=True,
                                            use_fix_fail_line=True,
                                            use_typical_issue_text=True,
                                            include_diffs=True,
                                        ),
                                        fixes=[
                                            AttemptEdge(
                                                pooling=(PoolingConfig(size=3)),
                                                k_top_config=KTopConfig(
                                                    k_top=5,
                                                    unique_code=False,
                                                    unique_output=False,
                                                ),
                                                configs=[
                                                    FixAttemptConfig(
                                                        attempts=5,
                                                        llm_config=LLMConfig(
                                                            model=model,
                                                            temperature=0.95,
                                                        ),
                                                        prompt_config=FixPromptConfig(
                                                            base_prompt=Prompt.REASONING,
                                                            use_ascii=True,
                                                            use_array=True,
                                                            use_image=False,
                                                            use_fix_reasoning_tags=True,
                                                            use_fix_fail_line=True,
                                                            use_typical_issue_text=True,
                                                            include_diffs=True,
                                                        ),
                                                        fixes=[],
                                                    )
                                                ],
                                            )
                                        ],
                                    )
                                ],
                            )
                        ],
                    )
                ],
            ),
        ],
    ),
]
small_tree: list[RootAttemptConfig] = [
    RootAttemptConfig(
        attempts=0,
        llm_config=LLMConfig(
            model=model,
            temperature=0.95,
        ),
        prompt_config=RootPromptConfig(
            base_prompt=Prompt.REASONING,
            use_examples=True,
            use_diffs=True,
            use_images=False,
            use_ascii=True,
            use_array=True,
            use_image=False,
        ),
        fixes=[],
    ),
    RootAttemptConfig(
        include_all_attempts_in_fixes=True,
        attempts=100,
        llm_config=LLMConfig(
            model=model,
            temperature=0.95,
        ),
        prompt_config=RootPromptConfig(
            base_prompt=Prompt.REASONING,
            use_examples=True,
            use_diffs=True,
            use_images=False,
            use_ascii=True,
            use_array=True,
            use_image=False,
        ),
        fixes=[
            AttemptEdge(
                k_top_config=KTopConfig(
                    k_top=5, unique_code=False, unique_output=False
                ),
                configs=[
                    FixAttemptConfig(
                        attempts=5,
                        llm_config=LLMConfig(
                            model=model,
                            temperature=0.95,
                        ),
                        prompt_config=FixPromptConfig(
                            base_prompt=Prompt.REASONING,
                            use_ascii=True,
                            use_array=True,
                            use_image=False,
                            use_fix_reasoning_tags=True,
                            use_fix_fail_line=True,
                            use_typical_issue_text=True,
                            include_diffs=True,
                        ),
                        fixes=[
                            AttemptEdge(
                                k_top_config=KTopConfig(
                                    k_top=5, unique_code=False, unique_output=False
                                ),
                                configs=[
                                    FixAttemptConfig(
                                        attempts=5,
                                        llm_config=LLMConfig(
                                            model=model,
                                            temperature=0.95,
                                        ),
                                        prompt_config=FixPromptConfig(
                                            base_prompt=Prompt.REASONING,
                                            use_ascii=True,
                                            use_array=True,
                                            use_image=False,
                                            use_fix_reasoning_tags=True,
                                            use_fix_fail_line=True,
                                            use_typical_issue_text=True,
                                            include_diffs=True,
                                        ),
                                        fixes=[],
                                    )
                                ],
                            )
                        ],
                    )
                ],
            ),
            AttemptEdge(
                pooling=(PoolingConfig(size=3)),
                k_top_config=KTopConfig(
                    k_top=5, unique_code=False, unique_output=False
                ),
                configs=[
                    FixAttemptConfig(
                        attempts=5,
                        llm_config=LLMConfig(
                            model=model,
                            temperature=0.95,
                        ),
                        prompt_config=FixPromptConfig(
                            base_prompt=Prompt.REASONING,
                            use_ascii=True,
                            use_array=True,
                            use_image=False,
                            use_fix_reasoning_tags=True,
                            use_fix_fail_line=True,
                            use_typical_issue_text=True,
                            include_diffs=True,
                        ),
                        fixes=[
                            AttemptEdge(
                                pooling=(PoolingConfig(size=3)),
                                k_top_config=KTopConfig(
                                    k_top=5, unique_code=False, unique_output=False
                                ),
                                configs=[
                                    FixAttemptConfig(
                                        attempts=5,
                                        llm_config=LLMConfig(
                                            model=model,
                                            temperature=0.95,
                                        ),
                                        prompt_config=FixPromptConfig(
                                            base_prompt=Prompt.REASONING,
                                            use_ascii=True,
                                            use_array=True,
                                            use_image=False,
                                            use_fix_reasoning_tags=True,
                                            use_fix_fail_line=True,
                                            use_typical_issue_text=True,
                                            include_diffs=True,
                                        ),
                                        fixes=[],
                                    )
                                ],
                            )
                        ],
                    )
                ],
            ),
        ],
    ),
]
